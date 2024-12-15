from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import modelformset_factory, inlineformset_factory
from django.utils.safestring import mark_safe

from .models import Survey, Question, QuestionType, ResponseChoice, SurveyResponse, Response, UserProfile
# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

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
            'img': forms.ClearableFileInput(attrs={'class': 'form-control', 'clear_checkbox_label ': None}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:  # Only apply defaults to new instances
            self.fields['question_type'].initial = 1  # Default value for question_type

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

class FormToAnswerSurvey(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super(FormToAnswerSurvey, self).__init__(*args, **kwargs)
        for question in questions:
            
            question_label = f''
            if(question.img):
                img_html = f'<br><img src="{question.img.url}" alt="Question Image" style="max-width:300px; max-height:300px;"><br>'
                question_label = img_html

            question_label += f"{question.question_order}. {question.question_text}"
            question_label = mark_safe(question_label)

            choices = ResponseChoice.objects.filter(question=question)
            if choices.exists():
                self.fields[f"question_{question.id}"] = forms.ChoiceField(
                    choices=[(choice.id, choice.choices_text) for choice in choices],
                    widget=forms.RadioSelect,
                    label=question_label,
                    required=True
                )
            else:
                self.fields[f"question_{question.id}"] = forms.CharField(
                    label=question_label,
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True
                )
                
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['picture', 'bio']

class FormToPublishSurvey(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['opening_time', 'closing_time', 'status']
        widgets = {
            'opening_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'closing_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    # Include full name in the form
    full_name = forms.CharField(max_length=100, required=False, label="Full Name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:  # If user instance exists, populate the full_name field
            self.fields['full_name'].initial = self.instance.user.get_full_name()
    class Meta:
        model = UserProfile
        fields = ['phone', 'bio', 'picture']  # Existing fields of UserProfile

