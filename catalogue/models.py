from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import date, timedelta


class Song(models.Model):
    title = models.CharField(max_length=512)
    running_time = models.PositiveIntegerField(
        help_text="Length of the song in seconds (≥ 10)")

    def clean(self):
        if self.running_time < 10:
            raise ValidationError(
                {'running_time': 'Song must be at least 10 seconds long.'})

    def __str__(self):
        return self.title


class Album(models.Model):
    FORMAT_CHOICES = [
        ('DD', 'Digital Download'),
        ('CD', 'CD'),
        ('VL', 'Vinyl'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    artist = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    format = models.CharField(max_length=2, choices=FORMAT_CHOICES)
    release_date = models.DateField()
    cover_image = models.ImageField(
        upload_to='album_covers/', blank=True, null=True, default='default_cover.jpg')
    slug = models.SlugField(blank=True, editable=False)
    tracks = models.ManyToManyField(Song, through='AlbumTracklistItem')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'artist', 'format'], name='unique_album_per_artist_format')
        ]

    def clean(self):
        max_future_date = date.today() + timedelta(days=3*365)
        if self.release_date > max_future_date:
            raise ValidationError(
                {'release_date': 'Release date cannot be more than 3 years in the future.'})
        if self.price < 0 or self.price > 999.99:
            raise ValidationError(
                {'price': 'Price must be between £0.00 and £999.99.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class AlbumTracklistItem(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('album', 'song')
        ordering = ['position']

    def __str__(self):
        return f"{self.song.title} in {self.album.title} (Position: {self.position})"


class MusicManagerUser(models.Model):
    PERMISSION_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('artist', 'Artist'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    def __str__(self):
        return f"{self.display_name} ({self.permission})"
