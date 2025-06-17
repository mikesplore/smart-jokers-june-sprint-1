from django import forms
from .models import AttendanceRecord

class CheckInForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['temperature', 'purpose_of_visit', 'comments']
        
class CheckOutForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea, required=False)