from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import Survey, Question, QuestionType, ResponseChoice

# Form to create a survey
class FormToCreateSurvey(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter survey title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 4}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:  # Only apply defaults to new instances
            self.fields['question_type'].initial = 1  # Default value for question_type

# Create a modelformset for Questions
questionsForm = modelformset_factory(
    Question,
    form=FormToCreateQuestion,  # Use the FormToCreateQuestion for customization
    extra=1,
)

# Form to create response choices
class FormToCreateChoices(forms.ModelForm):
    class Meta:
        model = ResponseChoice
        fields = ['choices_text']
        labels = {
            'choices_text': '',  # Remove the label
        }
        widgets = {
            'choices_text': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter choice text'
            })
        }


ChoiceInlineFormset = inlineformset_factory(
    Question,
    ResponseChoice,
    form=FormToCreateChoices,
    extra=1,
    can_delete=False  
)
