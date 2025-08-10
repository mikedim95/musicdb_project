from django.urls import path
from . import views
from . import api_views
from django.contrib.auth import views as auth_views
from catalogue.views import logout_then_home
urlpatterns = [
    # Web views
    path('', views.album_list_view, name='album_list'),
    path('albums/new/', views.create_album_view, name='create_album'),
    path('albums/<int:id>/', views.album_detail_view, name='album_detail'),
    path('albums/<int:id>/delete/', views.album_delete_view, name='album_delete'),
    path('albums/<int:id>/edit/', views.edit_album_view, name='album_edit'),
    path('albums/<int:id>/tracklist/add/',
         views.add_track_to_album_view, name='add_track'),
    path('albums/<int:album_id>/tracklist/<int:track_id>/edit/',
         views.edit_track_view, name='edit_track'),
    path('albums/<int:album_id>/tracklist/<int:track_id>/delete/',
         views.delete_track_view, name='delete_track'),
    path('albums/<int:id>/<slug:slug>/',
         views.album_detail_slug_view, name='album_detail_slug'),

    # API root
    path('api/', api_views.api_home, name="api_home"),

    # API - Songs
    path('api/songs/', api_views.api_songs, name="api_songs"),
    path('api/songs/<int:id>/', api_views.api_song_detail, name="api_song_detail"),

    # API - Albums
    path('api/albums/', api_views.api_albums, name="api_albums"),
    path('api/albums/<int:id>/', api_views.api_album_detail,
         name="api_album_detail"),

    # API - Tracklists
    path('api/tracklist/', api_views.api_tracklists, name="api_tracklists"),
    path('api/tracklist/<int:id>/', api_views.api_tracklist_detail,
         name="api_tracklist_detail"),
    path('accounts/login/', auth_views.LoginView.as_view(
         template_name='catalogue/login.html'), name='login'),
    path('accounts/logout/', logout_then_home, name='logout'),
]
