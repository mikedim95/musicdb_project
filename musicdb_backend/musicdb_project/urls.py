from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ✅ required
from django.conf import settings
from django.conf.urls.static import static
from catalogue.views import logout_then_home
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalogue.urls')),

    # ✅ Login/logout views
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='catalogue/login.html'), name='login'),
    path('accounts/logout/', logout_then_home, name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
