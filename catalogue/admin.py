from django.contrib import admin
from .models import Song, Album, AlbumTracklistItem, MusicManagerUser

admin.site.register(Song)
admin.site.register(Album)
admin.site.register(AlbumTracklistItem)
admin.site.register(MusicManagerUser)
