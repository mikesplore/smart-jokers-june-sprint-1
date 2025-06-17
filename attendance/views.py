from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncWeek, TruncMonth, ExtractHour
import json
from users.models import User
from .models import AttendanceRecord
from .forms import CheckInForm, CheckOutForm
from django.contrib import messages
import calendar
from datetime import timedelta, datetime

# Try to import REST Framework, but provide fallbacks if not installed
try:
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.permissions import IsAuthenticated
    REST_FRAMEWORK_AVAILABLE = True
except ImportError:
    REST_FRAMEWORK_AVAILABLE = False
    # Create stub classes/functions for compatibility
    def api_view(methods):
        def decorator(func):
            return func
        return decorator
    
    class Response(JsonResponse):
        def __init__(self, data, status=200):
            super().__init__(data=data, status=status)
    
    class status:
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_400_BAD_REQUEST = 400
        HTTP_404_NOT_FOUND = 404

# Import serializers only if REST Framework is available
if REST_FRAMEWORK_AVAILABLE:
    try:
        from .serializers import AttendanceRecordSerializer
    except ImportError:
        AttendanceRecordSerializer = None
else:
    AttendanceRecordSerializer = None


def check_in(request, user_id):
    user = get_object_or_404(User, id=user_id)
    today = timezone.now().date()
    
    attendance, created = AttendanceRecord.objects.get_or_create(
        user=user,
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
    
    return render(request, 'attendance/check_in.html', {
        'form': form,
        'user': user
    })

def check_out(request, user_id):
    user = get_object_or_404(User, id=user_id)
    today = timezone.now().date()
    
    try:
        attendance = AttendanceRecord.objects.get(
            user=user,
            date=today,
        )
    except AttendanceRecord.DoesNotExist:
        return render(request, 'attendance/not_checked_in.html', {'user': user})
    
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
    
    return render(request, 'attendance/check_out.html', {
        'form': form, 
        'attendance': attendance,
        'user': user
    })

def attendance_success(request):
    return render(request, 'attendance/success.html')

def attendance_list(request):
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=today).order_by('-check_in_time')
    return render(request, 'attendance/list.html', {'records': records})

def attendance_dashboard(request):
    """Dashboard view for the attendance app"""
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=today).order_by('-check_in_time')
    
    context = {
        'records': records,
        'today': today,
    }
    
    return render(request, 'attendance/dashboard.html', context)

def sign_attendance(request):
    """
    Public page for signing attendance (check-in or check-out).
    User enters email, then fills in the form.
    """
    # Add debug context to see what's happening
    context = {
        'debug': True,
        'request_method': request.method,
        'post_data': dict(request.POST.items()) if request.method == 'POST' else None,
    }
    
    if request.method == 'POST':
        email = request.POST.get('email')
        context['submitted_email'] = email
        
        # If email is not provided, show an error
        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, 'attendance/sign_attendance.html', context)

        try:
            # Rename user to attendance_user to avoid template confusion
            attendance_user = User.objects.get(email=email)
            context['attendance_user'] = attendance_user
        except User.DoesNotExist:
            messages.error(request, "No user found with that email.")
            context['email'] = email
            return render(request, 'attendance/sign_attendance.html', context)

        today = timezone.now().date()
        attendance, created = AttendanceRecord.objects.get_or_create(user=attendance_user, date=today)
        context['attendance'] = attendance
        context['created_new'] = created
        context['email'] = email

        # Handle check-in
        if not attendance.check_in_time:
            context['action'] = 'check_in'
            if 'check_in' in request.POST:
                form = CheckInForm(request.POST, instance=attendance)
                if form.is_valid():
                    record = form.save(commit=False)
                    record.check_in_time = timezone.now()
                    record.save()
                    messages.success(request, f"Successfully checked in at {record.check_in_time.strftime('%H:%M:%S')}")
                    return redirect('attendance_success')
            else:
                form = CheckInForm(instance=attendance)
            context['form'] = form
            return render(request, 'attendance/sign_attendance.html', context)

        # Handle check-out
        elif not attendance.check_out_time:
            context['action'] = 'check_out'
            if 'check_out' in request.POST:
                form = CheckOutForm(request.POST)
                if form.is_valid():
                    attendance.check_out_time = timezone.now()
                    if form.cleaned_data.get('comments'):
                        attendance.comments += f"\nCheck-out comments: {form.cleaned_data['comments']}"
                    attendance.save()
                    messages.success(request, f"Successfully checked out at {attendance.check_out_time.strftime('%H:%M:%S')}")
                    return redirect('attendance_success')
            else:
                form = CheckOutForm()
            context['form'] = form
            return render(request, 'attendance/sign_attendance.html', context)

        # Already checked in and out
        else:
            context['already_done'] = True
            return render(request, 'attendance/sign_attendance.html', context)

    # GET request - show the initial form
    return render(request, 'attendance/sign_attendance.html', context)

# API Endpoints
@csrf_exempt
@api_view(['POST'])
def api_check_in(request):
    """API endpoint for user check-in"""
    if not REST_FRAMEWORK_AVAILABLE:
        return JsonResponse({
            'error': 'Django REST Framework is not installed. Please install it first.'
        }, status=400)
        
    try:
        data = request.data
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        today = timezone.now().date()
        
        # Check if already checked in
        existing = AttendanceRecord.objects.filter(user=user, date=today).first()
        if existing and existing.check_in_time:
            return Response({
                'error': 'Already checked in',
                'check_in_time': existing.check_in_time
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new record or update existing
        if existing:
            attendance = existing
        else:
            attendance = AttendanceRecord(user=user, date=today)
        
        attendance.check_in_time = timezone.now()
        attendance.purpose_of_visit = data.get('purpose_of_visit', '')
        attendance.comments = data.get('comments', '')
        attendance.save()
        
        serializer = AttendanceRecordSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def api_check_out(request):
    """API endpoint for user check-out"""
    if not REST_FRAMEWORK_AVAILABLE:
        return JsonResponse({
            'error': 'Django REST Framework is not installed. Please install it first.'
        }, status=400)
        
    try:
        data = request.data
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        today = timezone.now().date()
        
        # Get today's record
        try:
            attendance = AttendanceRecord.objects.get(user=user, date=today)
        except AttendanceRecord.DoesNotExist:
            return Response({'error': 'No check-in record found for today'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already checked out
        if attendance.check_out_time:
            return Response({
                'error': 'Already checked out',
                'check_out_time': attendance.check_out_time
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update check-out time and comments
        attendance.check_out_time = timezone.now()
        if 'comments' in data and data['comments']:
            attendance.comments += f"\nCheck-out comments: {data['comments']}"
        attendance.save()
        
        serializer = AttendanceRecordSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_attendance_records(request):
    """API endpoint to get attendance records"""
    if not REST_FRAMEWORK_AVAILABLE:
        return JsonResponse({
            'error': 'Django REST Framework is not installed. Please install it first.'
        }, status=400)
        
    date_param = request.query_params.get('date')
    user_id = request.query_params.get('user_id')
    
    # Filter records
    records = AttendanceRecord.objects.all()
    
    if date_param:
        try:
            date = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
            records = records.filter(date=date)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        # Default to today if no date provided
        today = timezone.now().date()
        records = records.filter(date=today)
    
    if user_id:
        records = records.filter(user_id=user_id)
    
    serializer = AttendanceRecordSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_user_attendance(request, user_id):
    """API endpoint to get a specific user's attendance history"""
    if not REST_FRAMEWORK_AVAILABLE:
        return JsonResponse({
            'error': 'Django REST Framework is not installed. Please install it first.'
        }, status=400)
        
    try:
        user = User.objects.get(id=user_id)
        records = AttendanceRecord.objects.filter(user=user).order_by('-date')
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

def is_staff(user):
    """Check if user is staff"""
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def analytics_dashboard(request):
    """Analytics dashboard view for staff users only"""
    today = timezone.now().date()
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default to last 30 days if no date range specified
    if not date_from:
        date_from = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = today.strftime('%Y-%m-%d')
    
    try:
        filter_start = datetime.strptime(date_from, '%Y-%m-%d').date()
        filter_end = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        filter_start = today - timedelta(days=30)
        filter_end = today
    
    # Base queryset with date filter
    base_qs = AttendanceRecord.objects.filter(
        date__gte=filter_start,
        date__lte=filter_end
    )
    
    # Today's stats
    today_count = AttendanceRecord.objects.filter(date=today).count()
    today_checked_in = AttendanceRecord.objects.filter(date=today, check_in_time__isnull=False).count()
    today_checked_out = AttendanceRecord.objects.filter(date=today, check_out_time__isnull=False).count()
    
    # Date range stats
    total_records = base_qs.count()
    
    # Visits by user type
    user_type_counts = base_qs.values(
        'user__user_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily attendance trend
    daily_counts = base_qs.values(
        'date'
    ).annotate(
        count=Count('id')
    ).order_by('date')
    
    # Popular check-in hours
    hour_distribution = base_qs.filter(
        check_in_time__isnull=False
    ).annotate(
        hour=ExtractHour('check_in_time')
    ).values(
        'hour'
    ).annotate(
        count=Count('id')
    ).order_by('hour')
    
    # Purpose of visit analysis
    purpose_counts = base_qs.exclude(
        purpose_of_visit=''
    ).values(
        'purpose_of_visit'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]  # Top 10 purposes
    
    # Average visit duration
    visit_durations = base_qs.filter(
        check_in_time__isnull=False,
        check_out_time__isnull=False
    ).annotate(
        duration=F('check_out_time') - F('check_in_time')
    )
    
    # This is a bit more complex as we need to calculate the average ourselves
    total_seconds = 0
    valid_records = 0
    for record in visit_durations:
        # Convert duration to seconds
        seconds = record.duration.total_seconds()
        if seconds > 0:  # Filter out negative durations (data errors)
            total_seconds += seconds
            valid_records += 1
    
    avg_duration_minutes = 0
    if valid_records > 0:
        avg_duration_minutes = round(total_seconds / valid_records / 60)
    
    # Weekly trends
    weekly_counts = base_qs.annotate(
        week=TruncWeek('date')
    ).values(
        'week'
    ).annotate(
        count=Count('id')
    ).order_by('week')
    
    # Monthly trends
    monthly_counts = base_qs.annotate(
        month=TruncMonth('date')
    ).values(
        'month'
    ).annotate(
        count=Count('id')
    ).order_by('month')
    
    # Prepare data for charts
    chart_data = {
        'daily_labels': [entry['date'].strftime('%Y-%m-%d') for entry in daily_counts],
        'daily_counts': [entry['count'] for entry in daily_counts],
        'user_type_labels': [entry['user__user_type'] for entry in user_type_counts],
        'user_type_counts': [entry['count'] for entry in user_type_counts],
        'hour_labels': [f"{entry['hour']}:00" for entry in hour_distribution],
        'hour_counts': [entry['count'] for entry in hour_distribution],
        'purpose_labels': [entry['purpose_of_visit'] for entry in purpose_counts],
        'purpose_counts': [entry['count'] for entry in purpose_counts],
        'weekly_labels': [entry['week'].strftime('%Y-%m-%d') for entry in weekly_counts],
        'weekly_counts': [entry['count'] for entry in weekly_counts],
        'monthly_labels': [entry['month'].strftime('%Y-%m') for entry in monthly_counts],
        'monthly_counts': [entry['count'] for entry in monthly_counts],
    }
    
    context = {
        'today_count': today_count,
        'today_checked_in': today_checked_in,
        'today_checked_out': today_checked_out,
        'total_records': total_records,
        'avg_duration_minutes': avg_duration_minutes,
        'purpose_counts': purpose_counts,
        'chart_data': chart_data,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'attendance/analytics_dashboard.html', context)
