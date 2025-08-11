from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from catalogue.models import MusicManagerUser, Album, Song, AlbumTracklistItem


class Command(BaseCommand):
    help = "Reset DB and insert sample data (users, albums with covers, songs, tracks)."

    def handle(self, *args, **options):
        try:
            # 0) Fresh start
            self.stdout.write("💥 Flushing database...")
            call_command("flush", "--noinput")

            # 1) Users
            users_data = [
                {"username": "jason",      "password": "adminpass",  "is_superuser": True,
                    "is_staff": True,  "permission": "editor", "display_name": "Jason Admin"},
                {"username": "testArtist", "password": "artistpass", "is_superuser": False,
                    "is_staff": False, "permission": "artist", "display_name": "Test Artist"},
                {"username": "testEditor", "password": "editorpass", "is_superuser": False,
                    "is_staff": True,  "permission": "editor", "display_name": "Test Editor"},
                {"username": "testViewer", "password": "viewerpass", "is_superuser": False,
                    "is_staff": False, "permission": "viewer", "display_name": "Test Viewer"},
            ]
            for u in users_data:
                user, created = User.objects.get_or_create(
                    username=u["username"])
                if created:
                    user.set_password(u["password"])
                user.is_superuser = u["is_superuser"]
                user.is_staff = u["is_staff"]
                user.save()
                MusicManagerUser.objects.get_or_create(
                    user=user,
                    defaults={
                        "display_name": u["display_name"], "permission": u["permission"]},
                )
                self.stdout.write(
                    f"👤 {u['username']} ({u['permission']}) created.")

            # 2) Albums (+ explicit covers in media/)
            albums_data = [
                {"title": "Dripping Stereo", "description": "An eclectic mix of dripping sounds.", "artist": "Test Artist",
                    "price": 9.99,  "format": "DD", "release_date": date(2024, 5, 1),  "cover_file": "dripping-stereo.png"},
                {"title": "Music for Cats",  "description": "Soothing tunes for feline friends.", "artist": "Test Artist",
                    "price": 12.50, "format": "VL", "release_date": date(2023, 11, 15), "cover_file": "music-for-cats.png"},
                {"title": "My Red House",    "description": "Indie vibes from the red house.",     "artist": "Various Artists",
                    "price": 14.99, "format": "CD", "release_date": date(2020, 8, 20),  "cover_file": "my-red-house.png"},
            ]
            albums_map = {}
            for a in albums_data:
                album = Album.objects.create(
                    title=a["title"],
                    description=a["description"],
                    artist=a["artist"],
                    price=a["price"],
                    format=a["format"],
                    release_date=a["release_date"],
                )
                albums_map[a["title"]] = album
                # attach cover
                media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
                file_path = media_root / a["cover_file"]
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        album.cover_image.save(
                            a["cover_file"], File(f), save=True)
                    self.stdout.write(f"🖼  Cover set for {a['title']}")
                else:
                    self.stdout.write(
                        f"⚠ No cover found for {a['title']} ({a['cover_file']})")

            # 3) Songs
            songs_data = [
                {"title": "Track One",   "length": 180, "artist": "Test Artist"},
                {"title": "Track Two",   "length": 200, "artist": "Test Artist"},
                {"title": "Track Three", "length": 220, "artist": "Test Artist"},
                {"title": "Track Four",  "length": 210, "artist": "Test Artist"},
                {"title": "Track Five",  "length": 240,
                    "artist": "Various Artists"},
            ]
            songs_map = {}
            for s in songs_data:
                song = Song.objects.create(**s)
                songs_map[s["title"]] = song
                self.stdout.write(f"🎵 Song: {s['title']} ({s['length']}s)")

            # 4) Tracks (through model)
            tracks_data = [
                {"album": "Dripping Stereo", "song": "Track One",   "position": 1},
                {"album": "Dripping Stereo", "song": "Track Two",   "position": 2},
                {"album": "Music for Cats",  "song": "Track Three", "position": 1},
                {"album": "Music for Cats",  "song": "Track Four",  "position": 2},
                {"album": "My Red House",    "song": "Track Five",  "position": 1},
            ]
            for t in tracks_data:
                AlbumTracklistItem.objects.create(
                    album=albums_map[t["album"]],
                    song=songs_map[t["song"]],
                    position=t["position"],
                )
                self.stdout.write(
                    f"📀 Track: {t['album']} — {t['position']}. {t['song']}")

            # 5) Summary
            self.stdout.write(self.style.SUCCESS(
                f"\n📊 Counts: Users={User.objects.count()}, "
                f"MusicManagerUsers={MusicManagerUser.objects.count()}, "
                f"Albums={Album.objects.count()}, "
                f"Songs={Song.objects.count()}, "
                f"Tracks={AlbumTracklistItem.objects.count()}"
            ))

        except Exception as e:
            # surface any hidden exception (so it doesn't silently stop)
            import traceback
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(f"Seed failed: {e}"))
