from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'check_in_time', 'check_out_time', 'temperature', 'purpose_of_visit')
    list_filter = ('date', 'user__user_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'purpose_of_visit')
    date_hierarchy = 'date'
