from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('attendance/', include('attendance.urls')),
    # Redirect root URL to attendance dashboard
    path('', RedirectView.as_view(pattern_name='attendance_dashboard', permanent=False)),
    # If you have a users app with URLs
    path('users/', include('users.urls')),
]
