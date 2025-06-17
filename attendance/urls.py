from django.urls import path
from . import views


urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('check-in/<int:user_id>/', views.check_in, name='check_in'),
    path('check-out/<int:user_id>/', views.check_out, name='check_out'),
    path('success/', views.attendance_success, name='attendance_success'),
    path('list/', views.attendance_list, name='attendance_list'),
]
