from django import forms
from .models import Album, AlbumTracklistItem, Song


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'artist', 'description',
                  'release_date', 'price', 'cover_image']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'})
        }


class TracklistItemForm(forms.ModelForm):
    class Meta:
        model = AlbumTracklistItem
        fields = ['song', 'position']
