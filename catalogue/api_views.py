from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Song, Album, AlbumTracklistItem
import json

# Helper: shorten text for description_short


def _short(text, n=100):
    if not text:
        return ""
    return text[:n] + ("…" if len(text) > n else "")

# Helper: serialize album to match API samples


def _serialize_album(album, request):
    tracks = (AlbumTracklistItem.objects
              .filter(album=album)
              .select_related("song")
              .order_by("position", "id"))
    return {
        "id": album.id,
        "total_playtime": sum(t.song.length for t in tracks),
        "description_short": _short(album.description, 100),
        "release_year": album.release_date.year if album.release_date else None,
        "tracks": [{
            "id": t.song.id,
            "url": request.build_absolute_uri(
                reverse("api_song_detail", args=[t.song.id])
            ),
            "title": t.song.title,
            "length": t.song.length
        } for t in tracks],
        "url": request.build_absolute_uri(
            reverse("api_album_detail", args=[album.id])
        ),
        "cover_image": (
            request.build_absolute_uri(album.cover_image.url)
            if getattr(album, "cover_image", None) else ""
        ),
        "title": album.title,
        "description": album.description,
        "artist": album.artist,
        "price": str(album.price),
        "format": album.format,
        "release_date": album.release_date.isoformat() if album.release_date else None,
        "slug": album.slug,
    }

# Root API


def api_home(request):
    return JsonResponse({
        "albums": request.build_absolute_uri(reverse("api_albums")),
        "songs": request.build_absolute_uri(reverse("api_songs")),
        "tracklist": request.build_absolute_uri(reverse("api_tracklists")),
    })

# SONGS


@csrf_exempt
def api_songs(request):
    if request.method == "GET":
        data = [{
            "id": s.id,
            "url": request.build_absolute_uri(reverse("api_song_detail", args=[s.id])),
            "title": s.title,
            "length": s.length
        } for s in Song.objects.all()]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        song = Song.objects.create(
            title=data.get("title", ""),
            length=int(data.get("length", 10)),
            artist=data.get("artist", "Unknown Artist")
        )
        return JsonResponse({}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def api_song_detail(request, id):
    song = get_object_or_404(Song, id=id)

    if request.method == "GET":
        return JsonResponse({
            "id": song.id,
            "url": request.build_absolute_uri(reverse("api_song_detail", args=[song.id])),
            "title": song.title,
            "length": song.length
        })

    if request.method in ("PUT", "PATCH"):
        data = json.loads(request.body or "{}")
        if "title" in data:
            song.title = data["title"]
        if "length" in data:
            song.length = int(data["length"])
        song.save()
        return JsonResponse({
            "id": song.id,
            "url": request.build_absolute_uri(reverse("api_song_detail", args=[song.id])),
            "title": song.title,
            "length": song.length
        })

    if request.method == "DELETE":
        song.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


# ALBUMS
@csrf_exempt
def api_albums(request):
    if request.method == "GET":
        data = [_serialize_album(a, request) for a in Album.objects.all()]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        album = Album.objects.create(
            title=data.get("title", ""),
            description=data.get("description", ""),
            artist=data.get("artist", ""),
            price=data.get("price", 0),
            format=data.get("format", "DD"),
            release_date=data.get("release_date")
        )
        return JsonResponse({}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


def api_album_detail(request, id):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    album = get_object_or_404(Album, id=id)
    return JsonResponse(_serialize_album(album, request))


# TRACKLISTS
@csrf_exempt
def api_tracklists(request):
    if request.method == "GET":
        items = AlbumTracklistItem.objects.all().order_by("id")
        data = [{
            "id": t.id,
            "position": t.position,
            "song": t.song_id,
            "album": t.album_id,
        } for t in items]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        album = get_object_or_404(Album, id=data.get("album"))
        song = get_object_or_404(Song,  id=data.get("song"))

        # check uniqueness
        if AlbumTracklistItem.objects.filter(album=album, song=song).exists():
            return JsonResponse(
                {"error": "This song is already in that album."},
                status=400
            )

        item = AlbumTracklistItem.objects.create(
            album=album, song=song, position=data.get("position")
        )
        return JsonResponse({}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


def api_tracklist_detail(request, id):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    t = get_object_or_404(AlbumTracklistItem, id=id)
    return JsonResponse({
        "id": t.id,
        "position": t.position,
        "song": t.song_id,
        "album": t.album_id,
    })
