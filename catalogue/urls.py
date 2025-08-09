from django.urls import path
from .views import album_list_view, create_album_view, album_detail_view, album_delete_view, edit_album_view, add_track_to_album_view, edit_track_view, delete_track_view, album_detail_slug_view

from .api_views import api_songs, api_home, api_song_detail, api_albums, api_album_detail, api_tracklist, api_tracklist_detail, api_users, api_user_detail
urlpatterns = [
    path('', album_list_view, name='album_list'),
    path('api/', api_home, name='api_home'),
    path('albums/new/', create_album_view, name='create_album'),
    path('albums/<int:id>/', album_detail_view, name='album_detail'),
    path('albums/<int:id>/delete/', album_delete_view, name='album_delete'),
    path('albums/<int:id>/edit/', edit_album_view, name='album_edit'),
    path('albums/<int:id>/tracklist/add/',
         add_track_to_album_view, name='add_track'),
    path('albums/<int:album_id>/tracklist/<int:track_id>/edit/',
         edit_track_view, name='edit_track'),
    path('albums/<int:album_id>/tracklist/<int:track_id>/delete/',
         delete_track_view, name='delete_track'),
    path('albums/<int:id>/<slug:slug>/',
         album_detail_slug_view, name='album_detail_slug'),



    # API endpoints
    path('api/', api_home, name='api_home'),
    path('api/songs/', api_songs, name='api_songs'),
    path('api/songs/<int:id>/', api_song_detail, name='api_song_detail'),
    path("api/albums/", api_albums, name="api-albums"),
    path("api/albums/<int:id>/", api_album_detail, name="api-album-detail"),
    path("api/tracklist/", api_tracklist, name="api-tracklist"),
    path("api/tracklist/<int:id>/", api_tracklist_detail,
         name="api-tracklist-detail"),
    path("api/users/", api_users, name="api-users"),
    path("api/users/<int:id>/", api_user_detail, name="api-user-detail"),


]
