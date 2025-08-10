# load_sample_data.py
from catalogue.models import Song, Album, AlbumTracklistItem
import django
import os
import sys
import json
from pathlib import Path

# 1) Path setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 2) Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicdb_project.settings")

# 3) Setup Django BEFORE importing models
django.setup()

# 4) Now import models safely

# --- CLEAR OLD DATA (but keep users) ---
print("Deleting all albums, songs, and tracklist items...")
AlbumTracklistItem.objects.all().delete()
Album.objects.all().delete()
Song.objects.all().delete()

# --- LOAD NEW DATA ---
with open(BASE_DIR / "sample_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Songs
for s in data.get("songs", []):
    Song.objects.create(**s)
print(f"Loaded {Song.objects.count()} songs")

# Albums
for a in data.get("albums", []):
    Album.objects.create(**a)
print(f"Loaded {Album.objects.count()} albums")

# Tracklist items
for t in data.get("tracklists", []):
    AlbumTracklistItem.objects.create(**t)
print(f"Loaded {AlbumTracklistItem.objects.count()} tracklist items")

print("✅ Sample data loaded successfully!")
