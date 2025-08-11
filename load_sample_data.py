from django.contrib.auth.models import User
from catalogue.models import MusicManagerUser, Album, Song, AlbumTracklistItem
from datetime import date


def main():
    print("🗑 Clearing old data...")
    AlbumTracklistItem.objects.all().delete()
    Album.objects.all().delete()
    Song.objects.all().delete()
    MusicManagerUser.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    # --- USERS ---
    users_data = [
        {"username": "jason", "password": "adminpass", "is_superuser": True,
            "is_staff": True, "permission": "editor", "display_name": "Jason Admin"},
        {"username": "testArtist", "password": "artistpass", "is_superuser": False,
            "is_staff": False, "permission": "artist", "display_name": "Test Artist"},
        {"username": "testEditor", "password": "editorpass", "is_superuser": False,
            "is_staff": True, "permission": "editor", "display_name": "Test Editor"},
        {"username": "testViewer", "password": "viewerpass", "is_superuser": False,
            "is_staff": False, "permission": "viewer", "display_name": "Test Viewer"}
    ]

    user_map = {}
    for u in users_data:
        user = User.objects.create_user(
            username=u["username"], password=u["password"])
        user.is_superuser = u["is_superuser"]
        user.is_staff = u["is_staff"]
        user.save()
        mmu = MusicManagerUser.objects.create(
            user=user, display_name=u["display_name"], permission=u["permission"])
        user_map[u["username"]] = mmu
        print(f"👤 Created user: {u['username']} ({u['permission']})")

    # --- ALBUMS ---
    albums_data = [
        {"title": "Morning Sun", "description": "Bright and uplifting tracks to start the day.",
            "artist": "Test Artist", "price": 9.99, "format": "DD", "release_date": date(2024, 5, 1)},
        {"title": "Night Beats", "description": "Smooth evening tunes.", "artist": "Test Artist",
            "price": 12.50, "format": "VL", "release_date": date(2023, 11, 15)},
        {"title": "Golden Classics", "description": "A collection of timeless classics.",
            "artist": "Various Artists", "price": 14.99, "format": "CD", "release_date": date(2020, 8, 20)}
    ]

    albums_map = {}
    for a in albums_data:
        album = Album.objects.create(**a)
        albums_map[a["title"]] = album
        print(f"💿 Created album: {a['title']} by {a['artist']}")

    # --- SONGS ---
    songs_data = [
        {"title": "Sunrise Melody", "length": 180, "artist": "Test Artist"},
        {"title": "Coffee Groove", "length": 200, "artist": "Test Artist"},
        {"title": "Moonlight Dance", "length": 220, "artist": "Test Artist"},
        {"title": "City Lights", "length": 210, "artist": "Test Artist"},
        {"title": "Evergreen", "length": 240, "artist": "Various Artists"}
    ]

    songs_map = {}
    for s in songs_data:
        song = Song.objects.create(**s)
        songs_map[s["title"]] = song
        print(f"🎵 Created song: {s['title']} ({s['length']}s)")

    # --- TRACKS ---
    tracks_data = [
        {"album": "Morning Sun", "song": "Sunrise Melody", "position": 1},
        {"album": "Morning Sun", "song": "Coffee Groove", "position": 2},
        {"album": "Night Beats", "song": "Moonlight Dance", "position": 1},
        {"album": "Night Beats", "song": "City Lights", "position": 2},
        {"album": "Golden Classics", "song": "Evergreen", "position": 1}
    ]

    for t in tracks_data:
        AlbumTracklistItem.objects.create(
            album=albums_map[t["album"]], song=songs_map[t["song"]], position=t["position"])
        print(
            f"📀 Added track {t['position']} - {t['song']} to album {t['album']}")

    print("✅ Sample data loaded successfully.")


if __name__ == "__main__":
    main()
