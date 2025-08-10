from django.shortcuts import get_object_or_404
from .models import AlbumTracklistItem, Album
from django.shortcuts import render, redirect
from .forms import AlbumForm, TracklistItemForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    logout(request)  # removes session
    return redirect('album_list')  # send back to album list


def album_list_view(request):

    user = request.user

    if user.is_authenticated and hasattr(user, 'musicmanageruser'):
        mm_user = user.musicmanageruser
        print(f"User {user.username} has permission: {mm_user.permission}")
        if mm_user.permission == 'artist':
            albums = Album.objects.filter(artist=mm_user.display_name)
            print(
                f"Filtered albums for artist {mm_user.display_name}: {albums}")
        else:
            albums = Album.objects.all()
    else:
        albums = Album.objects.all()

    return render(request, 'catalogue/album_list.html', {'albums': albums})


def create_album_view(request):
    # Only allow Editors
    """ if not hasattr(request.user, 'musicmanageruser') or request.user.musicmanageruser.permission != 'editor':
        return HttpResponseForbidden("Only editors can create albums.") """

    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('album_list')
    else:
        form = AlbumForm()

    return render(request, 'catalogue/album_form.html', {'form': form})


def album_detail_view(request, id):
    album = get_object_or_404(Album, id=id)
    tracklist = AlbumTracklistItem.objects.filter(
        album=album)

    return render(request, 'catalogue/album_detail.html', {
        'album': album,
        'tracklist': tracklist
    })


@login_required
def album_edit_view(request, id):
    album = get_object_or_404(Album, id=id)

    mm_user = getattr(request.user, 'musicmanageruser', None)
    if not mm_user:
        raise PermissionDenied()

    # Check permissions
    if mm_user.permission == 'viewer':
        raise PermissionDenied()
    elif mm_user.permission == 'artist' and album.artist != mm_user.display_name:
        raise PermissionDenied()

    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            return redirect('album_list')
    else:
        form = AlbumForm(instance=album)

    return render(request, 'catalogue/album_form.html', {'form': form, 'edit': True})


@login_required
@require_http_methods(["GET", "POST"])
def album_delete_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = getattr(request.user, 'musicmanageruser', None)

    if not mm_user or mm_user.permission != 'editor':
        raise PermissionDenied()

    if request.method == 'POST':
        album.delete()
        return redirect('album_list')

    return render(request, 'catalogue/album_confirm_delete.html', {'album': album})


@login_required
def edit_album_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = getattr(request.user, 'musicmanageruser', None)

    if not mm_user or mm_user.permission != 'editor':
        raise PermissionDenied()

    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            return redirect('album_list')
    else:
        form = AlbumForm(instance=album)

    return render(request, 'catalogue/album_form.html', {
        'form': form,
        'editing': True,
        'album': album,
    })


@login_required
def add_track_to_album_view(request, id):
    album = get_object_or_404(Album, id=id)
    mm_user = getattr(request.user, 'musicmanageruser', None)

    # Permission: Editor OR Artist who owns this album
    if not mm_user or (
        mm_user.permission == 'artist' and mm_user.display_name != album.artist
    ) or mm_user.permission == 'viewer':
        raise PermissionDenied()

    if request.method == 'POST':
        form = TracklistItemForm(request.POST)
        if form.is_valid():
            track = form.save(commit=False)
            track.album = album
            track.save()
            return redirect('album_detail', id=album.id)
    else:
        form = TracklistItemForm()

    return render(request, 'catalogue/track_add.html', {
        'form': form,
        'album': album,
    })


@login_required
def edit_track_view(request, album_id, track_id):
    album = get_object_or_404(Album, id=album_id)
    track_item = get_object_or_404(
        AlbumTracklistItem, id=track_id, album=album)
    mm_user = getattr(request.user, 'musicmanageruser', None)

    if not mm_user or (
        mm_user.permission == 'artist' and mm_user.display_name != album.artist
    ) or mm_user.permission == 'viewer':
        raise PermissionDenied()

    if request.method == 'POST':
        form = TracklistItemForm(request.POST, instance=track_item)
        if form.is_valid():
            form.save()
            return redirect('album_detail', id=album.id)
    else:
        form = TracklistItemForm(instance=track_item)

    return render(request, 'catalogue/track_edit.html', {
        'form': form,
        'album': album,
        'track': track_item,
    })


@login_required
def delete_track_view(request, album_id, track_id):
    album = get_object_or_404(Album, id=album_id)
    track_item = get_object_or_404(
        AlbumTracklistItem, id=track_id, album=album)
    mm_user = getattr(request.user, 'musicmanageruser', None)

    if not mm_user or (
        mm_user.permission == 'artist' and mm_user.display_name != album.artist
    ) or mm_user.permission == 'viewer':
        raise PermissionDenied()

    if request.method == 'POST':
        track_item.delete()
        return redirect('album_detail', id=album.id)

    return render(request, 'catalogue/track_confirm_delete.html', {
        'album': album,
        'track':  track_item,
    })


@login_required
def album_detail_slug_view(request, id, slug):
    album = get_object_or_404(Album, id=id, slug=slug)
    return render(request, 'catalogue/album_detail.html', {
        'album': album,
    })
