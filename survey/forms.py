from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Survey, Question, QuestionType, ResponseChoice

# Form to create a survey
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

# Form to create questions
class FormToCreateQuestion(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'question_order', 'img']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'question_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
# Create a modelformset for Questions
questionsForm = modelformset_factory(
    Question,
    form=FormToCreateQuestion,  # Use the FormToCreateQuestion for customization
    extra=1,
    can_delete=True  # Allow deletion of forms
)

# Form to create response choices
class FormToCreateChoices(forms.ModelForm):
    class Meta:
        model = ResponseChoice
        fields = ['choices_text']
        widgets = {
            'choices_text': forms.Textarea(attrs={'class': 'form-control'})
        }

