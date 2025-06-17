from django import forms
from .models import AttendanceRecord

class CheckInForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['purpose_of_visit', 'comments']  # Removed temperature
        widgets = {
            # Removed temperature widget
            'purpose_of_visit': forms.TextInput(attrs={
                'placeholder': 'Why are you visiting today?',
                'class': 'form-control'
            }),
            'comments': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Any additional information...',
                'class': 'form-control'
            }),
        }
        
class CheckOutForm(forms.Form):
    comments = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': 'Any notes before leaving?',
            'class': 'form-control'
        }), 
        required=False
    )