from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/create/', views.UserCreateView.as_view(), name='user-create'),
    path('user/update/<int:pk>/', views.UserUpdateView.as_view(), name='user-update'),
    path('user/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user-delete'),
]