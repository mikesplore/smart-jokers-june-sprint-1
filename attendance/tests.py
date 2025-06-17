from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from users.models import User
from .models import AttendanceRecord
import datetime

class AttendanceTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            email="test@example.com",
            user_type="member",
            first_name="Test",
            last_name="User",
            phone_number="1234567890"
        )
        
    def test_check_in(self):
        # Test the check-in process
        client = Client()
        response = client.get(reverse('check_in', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        # Post check-in data
        data = {
            'temperature': 36.5,
            'purpose_of_visit': 'Testing',
            'comments': 'Test comment'
        }
        response = client.post(reverse('check_in', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Verify record created
        self.assertTrue(AttendanceRecord.objects.filter(user=self.user).exists())
