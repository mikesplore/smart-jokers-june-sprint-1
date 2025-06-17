from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from users.models import User
from .models import AttendanceRecord
import datetime
import json

class AttendanceTests(TestCase):
    def setUp(self):
        # Create a test user with password
        self.user = User.objects.create(
            email="test@example.com",
            user_type="member",
            first_name="Test",
            last_name="User",
            phone_number="1234567890"
        )
        self.user.set_password("testpassword")
        self.user.save()
        
        # Create a staff user
        self.staff_user = User.objects.create(
            email="staff@example.com",
            user_type="staff",
            first_name="Staff",
            last_name="User",
            phone_number="0987654321",
            is_staff=True
        )
        self.staff_user.set_password("staffpassword")
        self.staff_user.save()
        
        self.client = Client()
        self.api_client = APIClient()
        
    def test_check_in(self):
        # Test the check-in process
        response = self.client.get(reverse('check_in', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        # Post check-in data
        data = {
            'temperature': 36.5,
            'purpose_of_visit': 'Testing',
            'comments': 'Test comment'
        }
        response = self.client.post(reverse('check_in', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Verify record created
        self.assertTrue(AttendanceRecord.objects.filter(user=self.user).exists())
    
    def test_check_out(self):
        # Create check-in record first
        attendance = AttendanceRecord.objects.create(
            user=self.user,
            date=timezone.now().date(),
            check_in_time=timezone.now(),
            temperature=36.5,
            purpose_of_visit='Testing'
        )
        
        # Test check-out
        response = self.client.get(reverse('check_out', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        # Post check-out data
        data = {
            'comments': 'Checkout comment'
        }
        response = self.client.post(reverse('check_out', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        
        # Verify check-out time was set
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.check_out_time)
    
    def test_api_check_in(self):
        # Test API check-in
        data = {
            'user_id': self.user.id,
            'temperature': 36.5,
            'purpose_of_visit': 'API Testing',
            'comments': 'API test comment'
        }
        response = self.api_client.post(
            reverse('api_check_in'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify record created
        self.assertTrue(AttendanceRecord.objects.filter(
            user=self.user, 
            purpose_of_visit='API Testing'
        ).exists())
    
    def test_api_check_out(self):
        # Create check-in record first
        attendance = AttendanceRecord.objects.create(
            user=self.user,
            date=timezone.now().date(),
            check_in_time=timezone.now(),
            temperature=36.5,
            purpose_of_visit='API Testing'
        )
        
        # Test API check-out
        data = {
            'user_id': self.user.id,
            'comments': 'API checkout comment'
        }
        response = self.api_client.post(
            reverse('api_check_out'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify check-out time was set
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.check_out_time)
        self.assertIn('API checkout comment', attendance.comments)
    
    def test_staff_access_dashboard(self):
        # Login as staff user
        self.client.login(email='staff@example.com', password='staffpassword')
        
        # Staff should be able to access dashboard
        response = self.client.get(reverse('attendance_dashboard'))
        self.assertEqual(response.status_code, 200)

class AnalyticsDashboardTests(TestCase):
    def setUp(self):
        # Create a test user with password
        self.user = User.objects.create(
            email="test@example.com",
            user_type="member",
            first_name="Test",
            last_name="User",
            phone_number="1234567890"
        )
        self.user.set_password("testpassword")
        self.user.save()
        
        # Create a staff user
        self.staff_user = User.objects.create(
            email="staff@example.com",
            user_type="staff",
            first_name="Staff",
            last_name="User",
            phone_number="0987654321",
            is_staff=True
        )
        self.staff_user.set_password("staffpassword")
        self.staff_user.save()
        
        # Create test attendance records
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        # Today's records
        AttendanceRecord.objects.create(
            user=self.user,
            date=today,
            check_in_time=timezone.now(),
            temperature=36.5,
            purpose_of_visit="Meeting"
        )
        
        # Create a record for staff user
        record = AttendanceRecord.objects.create(
            user=self.staff_user,
            date=today,
            check_in_time=timezone.now() - timezone.timedelta(hours=3),
            temperature=36.2,
            purpose_of_visit="Work"
        )
        # Add checkout time
        record.check_out_time = timezone.now()
        record.save()
        
        # Yesterday's record
        AttendanceRecord.objects.create(
            user=self.user,
            date=yesterday,
            check_in_time=timezone.now() - timezone.timedelta(days=1),
            check_out_time=timezone.now() - timezone.timedelta(days=1, hours=-2),
            temperature=36.8,
            purpose_of_visit="Training"
        )
        
        self.client = Client()
    
    def test_analytics_dashboard_access_staff(self):
        """Test that staff users can access the analytics dashboard"""
        # Login as staff
        self.client.login(email='staff@example.com', password='staffpassword')
        
        # Access analytics dashboard
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/analytics_dashboard.html')
        
        # Check for analytics data in context
        self.assertIn('today_count', response.context)
        self.assertIn('chart_data', response.context)
    
    def test_analytics_dashboard_access_denied_regular_user(self):
        """Test that regular users cannot access the analytics dashboard"""
        # Login as regular user
        self.client.login(email='test@example.com', password='testpassword')
        
        # Attempt to access analytics dashboard
        response = self.client.get(reverse('analytics_dashboard'))
        # Should redirect to login
        self.assertNotEqual(response.status_code, 200)
    
    def test_analytics_dashboard_date_filter(self):
        """Test date filter functionality on analytics dashboard"""
        # Login as staff
        self.client.login(email='staff@example.com', password='staffpassword')
        
        # Get today and yesterday dates
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        # Test with date filter for just today
        response = self.client.get(
            reverse('analytics_dashboard'),
            {'date_from': today.strftime('%Y-%m-%d'), 'date_to': today.strftime('%Y-%m-%d')}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_records'], 2)  # Only today's records
        
        # Test with date filter for just yesterday
        response = self.client.get(
            reverse('analytics_dashboard'),
            {'date_from': yesterday.strftime('%Y-%m-%d'), 'date_to': yesterday.strftime('%Y-%m-%d')}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_records'], 1)  # Only yesterday's record
