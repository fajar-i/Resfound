from django import forms
from .models import Survey

class FormToCreateSurvey(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'opening_time', 'closing_time', 'total_price', 'status']
        widgets = {
            'opening_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'closing_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter survey title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 4}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }