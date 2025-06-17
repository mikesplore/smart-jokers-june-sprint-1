from django.db import models
from django.utils import timezone
from users.models import User


class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    purpose_of_visit = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True, default="")
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date', '-check_in_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"