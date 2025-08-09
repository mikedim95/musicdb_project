from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.apps import apps
from .models import Song, Album, AlbumTracklistItem, MusicManagerUser    # already present
import json
from datetime import datetime
from django.contrib.auth.models import User


def api_home(request):
    return JsonResponse({
        "message": "Music Manager API",
        "songs": "/api/songs/",
        "song_detail": "/api/songs/<id>/",
    })


@csrf_exempt
def api_songs(request):
    if request.method == "GET":
        data = [{
            "id": s.id,
            "title": s.title,
            "artist": getattr(s, "artist", None),
            "duration": s.duration,
        } for s in Song.objects.all()]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        song = Song.objects.create(
            title=data.get("title", ""),
            duration=int(data.get("duration", 10)),
            **({"artist": data.get("artist", "")} if hasattr(Song, "artist") else {})
        )
        return JsonResponse({"id": song.id}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def api_song_detail(request, id):
    song = get_object_or_404(Song, id=id)

    if request.method == "GET":
        return JsonResponse({
            "id": song.id,
            "title": song.title,
            "artist": getattr(song, "artist", None),
            "duration": song.duration,
        })

    if request.method in ("PUT", "PATCH"):
        data = json.loads(request.body or "{}")
        if "title" in data:
            song.title = data["title"]
        if "duration" in data:
            song.duration = int(data["duration"])
        if hasattr(Song, "artist") and "artist" in data:
            song.artist = data["artist"]
        song.save()
        return JsonResponse({"id": song.id})

    if request.method == "DELETE":
        song.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _serialize_album(a):
    # minimal, predictable payload
    return {
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "artist": a.artist,
        "price": a.price,
        "format": a.format,
        "release_date": a.release_date.isoformat() if a.release_date else None,
        "slug": a.slug,
    }


@csrf_exempt
def api_albums(request):
    if request.method == "GET":
        data = [_serialize_album(a) for a in Album.objects.all()]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        album = Album.objects.create(
            title=data.get("title", ""),
            description=data.get("description", ""),
            artist=data.get("artist", ""),
            price=data.get("price", 0),
            format=data.get("format", ""),
            release_date=_parse_date(data.get("release_date")),
            slug=data.get("slug", ""),
        )
        return JsonResponse({"id": album.id}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def api_album_detail(request, id):
    album = get_object_or_404(Album, id=id)

    if request.method == "GET":
        # include a super-plain tracklist if you have AlbumTracklistItem
        tracklist = []
        if 'AlbumTracklistItem' in globals():
            items = (AlbumTracklistItem.objects
                     .filter(album=album)
                     .select_related("song")
                     .order_by("position", "id"))
            for it in items:
                tracklist.append({
                    "id": it.id,
                    "position": it.position,
                    "song": it.song_id,
                })
        data = _serialize_album(album)
        data["tracklist"] = tracklist
        return JsonResponse(data)

    if request.method in ("PUT", "PATCH"):
        data = json.loads(request.body or "{}")
        if "title" in data:
            album.title = data["title"]
        if "description" in data:
            album.description = data["description"]
        if "artist" in data:
            album.artist = data["artist"]
        if "price" in data:
            album.price = data["price"]
        if "format" in data:
            album.format = data["format"]
        if "release_date" in data:
            album.release_date = _parse_date(data["release_date"])
        if "slug" in data:
            album.slug = data["slug"]
        album.save()
        return JsonResponse({"id": album.id})

    if request.method == "DELETE":
        album.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


@csrf_exempt
def api_tracklist(request):
    if request.method == "GET":
        items = AlbumTracklistItem.objects.select_related(
            "album", "song").all().order_by("position", "id")
        data = [{
            "id": i.id,
            "album": i.album_id,
            "album_title": i.album.title,
            "song": i.song_id,
            "song_title": i.song.title,
            "duration": i.song.duration,  # using 'duration' instead of running_time
            "position": i.position
        } for i in items]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        album = get_object_or_404(Album, id=data.get("album"))
        song = get_object_or_404(Song, id=data.get("song"))
        item = AlbumTracklistItem.objects.create(
            album=album,
            song=song,
            position=data.get("position")
        )
        return JsonResponse({"id": item.id}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def api_tracklist_detail(request, id):
    item = get_object_or_404(AlbumTracklistItem, id=id)

    if request.method == "GET":
        return JsonResponse({
            "id": item.id,
            "album": item.album_id,
            "album_title": item.album.title,
            "song": item.song_id,
            "song_title": item.song.title,
            "duration": item.song.duration,
            "position": item.position
        })

    if request.method in ("PUT", "PATCH"):
        data = json.loads(request.body or "{}")
        if "album" in data:
            item.album = get_object_or_404(Album, id=data["album"])
        if "song" in data:
            item.song = get_object_or_404(Song, id=data["song"])
        if "position" in data:
            item.position = data["position"]
        item.save()
        return JsonResponse({"id": item.id})

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


def _serialize_user(u):
    # Profile is optional
    try:
        p = u.musicmanageruser
        profile = {
            "display_name": p.display_name,
            "permission": p.permission,
        }
    except MusicManagerUser.DoesNotExist:
        profile = None

    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "is_staff": u.is_staff,
        "is_superuser": u.is_superuser,
        "profile": profile,
    }


@csrf_exempt
def api_users(request):
    if request.method == "GET":
        users = User.objects.all().select_related("musicmanageruser")
        return JsonResponse([_serialize_user(u) for u in users], safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        # create the auth user
        user = User.objects.create_user(
            username=data.get("username", "").strip(),
            email=data.get("email", "").strip(),
            password=data.get("password") or None,
        )
        user.is_staff = bool(data.get("is_staff", False))
        user.is_superuser = bool(data.get("is_superuser", False))
        user.save()

        # optional profile
        prof = data.get("profile") or {}
        if prof:
            MusicManagerUser.objects.create(
                user=user,
                display_name=prof.get("display_name", user.username),
                permission=prof.get("permission", "viewer"),
            )

        return JsonResponse({"id": user.id}, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def api_user_detail(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == "GET":
        return JsonResponse(_serialize_user(user))

    if request.method in ("PUT", "PATCH"):
        data = json.loads(request.body or "{}")

        # core user fields
        if "username" in data:
            user.username = data["username"].strip()
        if "email" in data:
            user.email = data["email"].strip()
        if "password" in data and data["password"]:
            user.set_password(data["password"])
        if "is_staff" in data:
            user.is_staff = bool(data["is_staff"])
        if "is_superuser" in data:
            user.is_superuser = bool(data["is_superuser"])
        user.save()

        # profile upsert
        prof = data.get("profile")
        if prof is not None:
            profile, _ = MusicManagerUser.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": prof.get("display_name", user.username),
                    "permission": prof.get("permission", "viewer"),
                },
            )
            if "display_name" in prof:
                profile.display_name = prof["display_name"]
            if "permission" in prof:
                profile.permission = prof["permission"]
            profile.save()

        return JsonResponse({"id": user.id})

    if request.method == "DELETE":
        user.delete()  # profile will cascade due to OneToOne on User with on_delete=CASCADE
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])
