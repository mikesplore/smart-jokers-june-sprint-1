from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User
import json

class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'user_type': 'member',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890'
        }
        self.user = User.objects.create(**self.user_data)
    
    def test_get_user(self):
        """Test retrieving a user"""
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
    
    def test_create_user(self):
        """Test creating a new user"""
        url = reverse('user-create')
        new_user_data = {
            'email': 'new@example.com',
            'user_type': 'visitor',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '9876543210'
        }
        response = self.client.post(url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email='new@example.com').first_name, 'New')
    
    def test_update_user(self):
        """Test updating a user"""
        url = reverse('user-update', args=[self.user.id])
        updated_data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_delete_user(self):
        """Test deleting a user"""
        url = reverse('user-delete', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
