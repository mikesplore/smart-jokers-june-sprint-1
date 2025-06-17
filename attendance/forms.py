from django import forms
from .models import AttendanceRecord

class CheckInForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['temperature', 'purpose_of_visit', 'comments']
        widgets = {
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'e.g., 36.5'}),
            'purpose_of_visit': forms.TextInput(attrs={'placeholder': 'Why are you visiting today?'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional information...'}),
        }
        
class CheckOutForm(forms.Form):
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes before leaving?'}), 
        required=False
    )