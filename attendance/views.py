from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.models import User
from .models import AttendanceRecord
from .forms import CheckInForm, CheckOutForm

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
