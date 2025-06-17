from django.urls import path
from .views import user_detail, user_create, user_update, user_delete, UserProfileView

urlpatterns = [
    path('user/<int:pk>/', user_detail, name='user-detail'),
    path('user/create/', user_create, name='user-create'),
    path('user/update/<int:pk>/', user_update, name='user-update'),
    path('user/delete/<int:pk>/', user_delete, name='user-delete'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile-detail'),
]