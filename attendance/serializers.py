from rest_framework import serializers
from users.models import User
from .models import AttendanceRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'user', 'user_details', 'date', 'check_in_time', 'check_out_time',
                  'temperature', 'purpose_of_visit', 'comments']
        read_only_fields = ['date', 'check_in_time', 'check_out_time']