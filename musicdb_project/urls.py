from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ✅ required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalogue.urls')),

    # ✅ Login/logout views
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='catalogue/login.html'), name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
