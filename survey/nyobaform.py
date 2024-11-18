from django import forms
from django.forms import modelformset_factory
from .models import Survey, Question, QuestionType, ResponseChoice

class YourForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'question_order', 'img']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'question_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
YourFormSet = modelformset_factory(Question, form=YourForm, extra=1, can_delete=True)
