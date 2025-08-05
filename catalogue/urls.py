from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.index, name='home'),
    path('api/', api_views.api_home),
]
