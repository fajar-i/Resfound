from django import forms
from .models import UserProfile
from django.contrib.auth.forms import AuthenticationForm
from django.forms import modelformset_factory, inlineformset_factory
from .models import Survey, Question, QuestionType, ResponseChoice, SurveyResponse, Response


from .models import UserSettings
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
            'img': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
            question_label = f"{question.question_order}. {question.question_text}"
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

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings  # Use your model here
        fields = ['setting_1', 'setting_2']