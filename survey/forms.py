from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import modelformset_factory, inlineformset_factory
from .models import Survey, Question, QuestionType, ResponseChoice, SurveyResponse, Response
from django.utils.safestring import mark_safe
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

class FormToPublishSurvey():
    class Meta:
        model = Survey
        fields = ['opening_time', 'closing_time', 'respoint', 'status']
        widgets = {
            'opening_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'placeholder': 'Select opening time'
                }
            ),
            'closing_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'placeholder': 'Select closing time'
                }
            ),
            'respoint': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Apply as many respoint'
                }
            ),
            'status': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }

        def respoint_rule(self):
            respoint = self.cleaned_data.get('respoint_by_user')

            if not self.survey_instance or not self.user:
                raise forms.ValidationError("Invalid survey or user context for validation.")

            survey_price = self.survey_instance.total_price
            user_profile = getattr(self.user, 'profile', None)

            if not user_profile:
                raise forms.ValidationError("User does not have a profile.")

            user_max_respoint = user_profile.respoint

            if respoint is not None:
                if respoint <= 0:
                    raise forms.ValidationError("Respoint can't be 0")
                
                if respoint > user_max_respoint:
                    raise forms.ValidationError("Insufficient Respoint")
                
                if total_price % survey_price != 0:
                    raise forms.ValidationError("Respoint must be a multiple of this survey price")
        
            return respoint
        

    def __init__(self, *args, **kwargs):
        # Get the user and survey instance from the form initialization
        self.user = kwargs.pop('user', None)
        self.survey_instance = kwargs.pop('instance', None)
        super(FormToPublishSurvey, self).__init__(*args, **kwargs)