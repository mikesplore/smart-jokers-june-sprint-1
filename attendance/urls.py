from django.urls import path
from . import views


urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('sign/', views.sign_attendance, name='sign_attendance'),
    path('check-in/<int:user_id>/', views.check_in, name='check_in'),
    path('check-out/<int:user_id>/', views.check_out, name='check_out'),
    path('success/', views.attendance_success, name='attendance_success'),
    path('list/', views.attendance_list, name='attendance_list'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # API endpoints
    path('api/check-in/', views.api_check_in, name='api_check_in'),
    path('api/check-out/', views.api_check_out, name='api_check_out'),
    path('api/records/', views.api_attendance_records, name='api_attendance_records'),
    path('api/user/<int:user_id>/attendance/', views.api_user_attendance, name='api_user_attendance'),
]
