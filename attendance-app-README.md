# Attendance App Implementation Guide

## Overview
The Attendance App will track daily sign-ins and sign-outs for both staff and community members. This document provides detailed instructions for implementing the attendance tracking functionality.

## Setup Instructions

1. Ensure you're working within the Django project structure that has the `attendance` app created:
   ```bash
   python manage.py startapp attendance
   ```

2. Add the attendance app to your `INSTALLED_APPS` in settings.py:
   ```python
   INSTALLED_APPS = [
       # ...other apps
       'attendance',
   ]
   ```

## Model Design

Create the following models in `attendance/models.py`:

```python
from django.db import models
from django.utils import timezone
from users.models import User

class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    
    # Optional fields from the daily sign-in form
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    purpose_of_visit = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', '-check_in_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
```

## Forms

Create forms in `attendance/forms.py`:

```python
from django import forms
from .models import AttendanceRecord

class CheckInForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['temperature', 'purpose_of_visit', 'comments']
        
class CheckOutForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea, required=False)
```

## Views Implementation

Create the following views in `attendance/views.py`:

```python
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AttendanceRecord
from .forms import CheckInForm, CheckOutForm

@login_required
def check_in(request):
    today = timezone.now().date()
    
    # Check if user already checked in today
    attendance, created = AttendanceRecord.objects.get_or_create(
        user=request.user,
        date=today,
    )
    
    if attendance.check_in_time and not created:
        return render(request, 'attendance/already_checked_in.html', {'attendance': attendance})
    
    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.check_in_time = timezone.now()
            attendance.save()
            return redirect('attendance_success')
    else:
        form = CheckInForm(instance=attendance)
    
    return render(request, 'attendance/check_in.html', {'form': form})

@login_required
def check_out(request):
    today = timezone.now().date()
    
    try:
        attendance = AttendanceRecord.objects.get(
            user=request.user,
            date=today,
        )
    except AttendanceRecord.DoesNotExist:
        return render(request, 'attendance/not_checked_in.html')
    
    if attendance.check_out_time:
        return render(request, 'attendance/already_checked_out.html', {'attendance': attendance})
    
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            attendance.check_out_time = timezone.now()
            if form.cleaned_data['comments']:
                attendance.comments += f"\nCheck-out comments: {form.cleaned_data['comments']}"
            attendance.save()
            return redirect('attendance_success')
    else:
        form = CheckOutForm()
    
    return render(request, 'attendance/check_out.html', {'form': form, 'attendance': attendance})

@login_required
def attendance_success(request):
    return render(request, 'attendance/success.html')
```

## API Endpoints

Create API views in `attendance/api.py`:

```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return AttendanceRecord.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        today = timezone.now().date()
        
        # Check if already checked in
        try:
            attendance = AttendanceRecord.objects.get(
                user=request.user,
                date=today
            )
            if attendance.check_in_time:
                return Response(
                    {"detail": "Already checked in today"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except AttendanceRecord.DoesNotExist:
            attendance = AttendanceRecord(user=request.user, date=today)
        
        # Update with data from request
        attendance.check_in_time = timezone.now()
        if 'temperature' in request.data:
            attendance.temperature = request.data['temperature']
        if 'purpose_of_visit' in request.data:
            attendance.purpose_of_visit = request.data['purpose_of_visit']
        if 'comments' in request.data:
            attendance.comments = request.data['comments']
        
        attendance.save()
        serializer = AttendanceRecordSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        today = timezone.now().date()
        
        try:
            attendance = AttendanceRecord.objects.get(
                user=request.user,
                date=today
            )
            
            if not attendance.check_in_time:
                return Response(
                    {"detail": "You need to check in first"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if attendance.check_out_time:
                return Response(
                    {"detail": "Already checked out today"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            attendance.check_out_time = timezone.now()
            
            if 'comments' in request.data:
                if attendance.comments:
                    attendance.comments += f"\nCheck-out comments: {request.data['comments']}"
                else:
                    attendance.comments = request.data['comments']
            
            attendance.save()
            serializer = AttendanceRecordSerializer(attendance)
            return Response(serializer.data)
            
        except AttendanceRecord.DoesNotExist:
            return Response(
                {"detail": "No check-in record found for today"},
                status=status.HTTP_404_NOT_FOUND
            )
```

Create serializers in `attendance/serializers.py`:

```python
from rest_framework import serializers
from .models import AttendanceRecord

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'user', 'date', 'check_in_time', 'check_out_time', 
                  'temperature', 'purpose_of_visit', 'comments']
        read_only_fields = ['user', 'date', 'check_in_time', 'check_out_time']
```

## URL Configuration

Add the following to `attendance/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

router = DefaultRouter()
router.register(r'records', api.AttendanceRecordViewSet, basename='attendance')

urlpatterns = [
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('success/', views.attendance_success, name='attendance_success'),
    path('api/', include(router.urls)),
]
```

Don't forget to include these URLs in your project's main `urls.py`.

## Templates

Create the following template files:

1. `attendance/templates/attendance/check_in.html` - Form for checking in
2. `attendance/templates/attendance/check_out.html` - Form for checking out
3. `attendance/templates/attendance/success.html` - Success page
4. `attendance/templates/attendance/already_checked_in.html` - Message when already checked in
5. `attendance/templates/attendance/already_checked_out.html` - Message when already checked out
6. `attendance/templates/attendance/not_checked_in.html` - Message when trying to check out without checking in

## Testing Guidelines

Create the following tests in `attendance/tests.py`:

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import AttendanceRecord
import json

User = get_user_model()

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
    def test_attendance_creation(self):
        attendance = AttendanceRecord.objects.create(
            user=self.user,
            date=timezone.now().date(),
            check_in_time=timezone.now()
        )
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        self.assertEqual(attendance.user, self.user)

class AttendanceViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
    def test_check_in_view(self):
        response = self.client.get(reverse('check_in'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('check_in'), {
            'temperature': '36.5',
            'purpose_of_visit': 'Work',
            'comments': 'Test comment'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        
    def test_check_out_view(self):
        # Create a check-in record first
        AttendanceRecord.objects.create(
            user=self.user,
            date=timezone.now().date(),
            check_in_time=timezone.now()
        )
        
        response = self.client.get(reverse('check_out'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('check_out'), {
            'comments': 'Leaving early'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        attendance = AttendanceRecord.objects.get(user=self.user)
        self.assertIsNotNone(attendance.check_out_time)

class AttendanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_check_in_api(self):
        response = self.client.post(reverse('attendance-check-in'), {
            'temperature': '36.5',
            'purpose_of_visit': 'Work',
            'comments': 'API test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        
    def test_check_out_api(self):
        # Create a check-in record first
        AttendanceRecord.objects.create(
            user=self.user,
            date=timezone.now().date(),
            check_in_time=timezone.now()
        )
        
        response = self.client.post(reverse('attendance-check-out'), {
            'comments': 'Leaving via API'
        })
        self.assertEqual(response.status_code, 200)
        
        attendance = AttendanceRecord.objects.get(user=self.user)
        self.assertIsNotNone(attendance.check_out_time)
```

## Admin Configuration

Add the following to `attendance/admin.py`:

```python
from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'check_in_time', 'check_out_time', 'temperature', 'purpose_of_visit')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'purpose_of_visit', 'comments')
    date_hierarchy = 'date'
```

## Running Tests

Run your tests with:

```bash
python manage.py test attendance
```

This will ensure your attendance app is working correctly.
