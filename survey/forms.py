from django import forms
from .models import Survey, Question, QuestionType

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

class FormToAddQuestion(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'question_order', 'img']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question text'}),
            # 'question_type': forms.Select(attrs={'class': 'form-control'}),
            'question_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'img': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super(FormToAddQuestion, self).__init__(*args, **kwargs)
    #     # Add dynamic choices from the database
    #     queryset_choices = [(qt.id, qt.name) for qt in QuestionType.objects.all()]
        
    #     # Set the choices for the field
    #     self.fields['question_type'].choices = queryset_choices