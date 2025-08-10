from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.shortcuts import redirect
from .forms import AlbumForm, TracklistItemForm
from .models import Album, AlbumTracklistItem, Song

# ---- helpers --------------------------------------------------------------


def _mm_user(request):
    """Return attached MusicManagerUser or None."""
    user = getattr(request, "user", None)
    return getattr(user, "musicmanageruser", None) if (user and user.is_authenticated) else None


def _can_edit_album(mm_user, album: Album) -> bool:
    if not mm_user:
        return False
    if mm_user.permission == "editor":
        return True
    if mm_user.permission == "artist" and album.artist == mm_user.display_name:
        return True
    return False


def _can_delete_album(mm_user, album: Album) -> bool:
    # Only editors can delete (per brief / mockups)
    return bool(mm_user and mm_user.permission == "editor")


def _artist_only_queryset(mm_user):
    """Return queryset for album list respecting role (artist sees only theirs)."""
    if not mm_user:
        return Album.objects.none()
    if mm_user.permission == "artist":
        return Album.objects.filter(artist=mm_user.display_name)
    # editor & viewer see all
    return Album.objects.all()

# ---- list / detail --------------------------------------------------------


# catalogue/views.py

def album_list_view(request):
    mm_user = _mm_user(request)
    qs = _artist_only_queryset(mm_user).order_by("title", "id")

    albums = list(qs)
    for a in albums:
        # editor OR owning artist
        a.can_edit = _can_edit_album(mm_user, a)
        a.can_delete = bool(mm_user and mm_user.permission ==
                            "editor")  # editors only

    return render(request, "catalogue/album_list.html", {
        "albums": albums,
        "mm_user": mm_user,
        "can_create": bool(mm_user and mm_user.permission == "editor"),
    })


def album_detail_view(request, id):
    album = get_object_or_404(Album, id=id)
    tracklist = AlbumTracklistItem.objects.filter(album=album)\
        .select_related("song").order_by("position", "id")
    mm_user = _mm_user(request)
    # editor OR owning artist
    can_edit = _can_edit_album(mm_user, album)
    can_delete = bool(mm_user and mm_user.permission ==
                      "editor")  # editors only
    print(f"can_edit: {can_edit}, can_delete: {can_delete}")
    return render(request, "catalogue/album_detail.html", {
        "album": album,
        "tracklist": tracklist,
        "mm_user": mm_user,
        "can_edit": can_edit,
        "can_delete": can_delete,
    })

# ---- create / edit / delete -----------------------------------------------


@login_required
@require_http_methods(["GET", "POST"])
def create_album_view(request):
    mm_user = _mm_user(request)
    if not mm_user or mm_user.permission != "editor":
        raise PermissionDenied()

    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save()
            messages.success(request, "Album created successfully")
            return redirect("album_detail", id=album.id)
    else:
        form = AlbumForm()

    return render(request, "catalogue/album_form.html", {
        "form": form,
        "is_create": True,
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_album_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = _mm_user(request)
    if not _can_edit_album(mm_user, album):
        raise PermissionDenied()

    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, "Album updated successfully")
            return redirect("album_detail", id=album.id)
    else:
        form = AlbumForm(instance=album)

    return render(request, "catalogue/album_form.html", {
        "form": form,
        "album": album,
        "is_edit": True,
    })


@login_required
@require_http_methods(["GET", "POST"])
def album_delete_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = _mm_user(request)
    if not _can_delete_album(mm_user, album):
        raise PermissionDenied()

    if request.method == "POST":
        title = album.title
        album.delete()
        messages.success(request, "Album deleted successfully")
        return redirect("album_list")

    # GET → show confirmation page
    return render(request, "catalogue/album_confirm_delete.html", {"album": album})

# ---- tracklist CRUD -------------------------------------------------------


@login_required
@require_http_methods(["GET", "POST"])
def add_track_to_album_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = _mm_user(request)
    if not _can_edit_album(mm_user, album):   # editors + owning artist
        raise PermissionDenied()

    if request.method == "POST":
        form = TracklistItemForm(request.POST)
        if form.is_valid():
            tli = form.save(commit=False)
            tli.album = album
            # prevent duplicates (album, song) unique_together
            exists = AlbumTracklistItem.objects.filter(
                album=album, song=tli.song).exists()
            if exists:
                messages.error(request, "That song is already in this album.")
            else:
                tli.save()
                messages.success(request, "Song added to album")
                return redirect("album_detail", id=album.id)
    else:
        form = TracklistItemForm()

    return render(request, "catalogue/track_add.html", {"form": form, "album": album})


@login_required
@require_http_methods(["GET", "POST"])
def edit_track_view(request, album_id, track_id):
    album = get_object_or_404(Album, id=album_id)
    tli = get_object_or_404(AlbumTracklistItem, id=track_id, album=album)
    mm_user = _mm_user(request)
    if not _can_edit_album(mm_user, album):
        raise PermissionDenied()

    if request.method == "POST":
        form = TracklistItemForm(request.POST, instance=tli)
        if form.is_valid():
            form.save()
            messages.success(request, "Track updated")
            return redirect("album_detail", id=album.id)
    else:
        form = TracklistItemForm(instance=tli)

    return render(request, "catalogue/track_edit.html", {"form": form, "album": album, "track": tli})


@login_required
@require_http_methods(["GET", "POST"])
def delete_track_view(request, album_id, track_id):
    album = get_object_or_404(Album, id=album_id)
    tli = get_object_or_404(AlbumTracklistItem, id=track_id, album=album)
    mm_user = _mm_user(request)
    if not _can_edit_album(mm_user, album):
        raise PermissionDenied()

    if request.method == "POST":
        tli.delete()
        messages.success(request, "Track removed")
        return redirect("album_detail", id=album.id)

    return render(request, "catalogue/track_confirm_delete.html", {"album": album, "track": tli})

# optional: slug detail (kept simple)


def album_detail_slug_view(request, id, slug):
    album = get_object_or_404(Album, id=id, slug=slug)
    return album_detail_view(request, id=album.id)


@require_http_methods(["GET", "POST"])
def logout_then_home(request):
    logout(request)
    return redirect('/')


def edit_track_view(request, album_id, track_id):
    album = get_object_or_404(Album, id=album_id)
    track = get_object_or_404(AlbumTracklistItem, id=track_id, album=album)
    songs = Song.objects.all()

    if request.method == "POST":
        song_id = request.POST.get("song")
        position = request.POST.get("position")
        track.song = get_object_or_404(Song, id=song_id)
        track.position = int(position)
        track.save()
        return redirect("album_detail", id=album.id)

    return render(request, "catalogue/track_edit.html", {
        "album": album,
        "track": track,
        "songs": songs
    })
