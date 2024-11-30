from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch, Max
from django.urls import reverse
from django.forms import modelformset_factory
from django.contrib.auth.models import User

from .models import Survey, Question, QuestionType, SurveyResponse, Response, ResponseChoice
from .forms import FormToCreateSurvey, FormToCreateQuestion, ChoiceInlineFormset, FormToAnswerSurvey

def home(request):
    return render(request, 'home.html')

def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'my_survey.html', {'surveys': list_semua})

def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        survey_name = survey.title
        survey.delete()
        messages.warning(request, f"Survey '{survey_name}' has been successfully deleted")
    else:
        messages.error(request, "Invalid request. Surveys can only be deleted through POST requests")
    return redirect('list_my_survey')

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST' or 'GET':
        survey = question.survey  # Get the related survey
        question.delete()  # Delete the question
        return redirect('edit_survey', survey_id=survey.id)
    else:
        return redirect('edit_survey', survey_id=question.survey.id)
        
def create_survey(request, survey_id=None):
    # Retrieve existing survey or initialize for creation
    survey = get_object_or_404(Survey, pk=survey_id) if survey_id else None
    is_edit_survey = survey is not None

    # Initialize survey form
    survey_form = FormToCreateSurvey(
        request.POST or None,
        instance=survey
    )

    # Adjust extra forms based on existing questions
    extra_forms = 0 if survey and survey.questions.exists() else 1
    QuestionFormSet = modelformset_factory(
        Question,
        form=FormToCreateQuestion,
        extra=extra_forms,
        can_delete=True
    )

    question_formset = QuestionFormSet(
        request.POST or None,
        request.FILES or None,
        queryset=survey.questions.all() if survey else Question.objects.none()
    )

    if request.method == 'POST':
        if survey_form.is_valid() and question_formset.is_valid():
            # Save survey instance
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()

            # Save questions
            question_mapping = {}

            for i, question_form in enumerate(question_formset):
                if question_form.cleaned_data.get('DELETE'):
                    # Handle deletion
                    if question_form.instance.pk:
                        question_form.instance.delete()
                else:
                    question = question_form.save(commit=False)
                    question.survey = survey
                    if question.question_text:
                        question.save()
                        question_mapping[f"form-{i}"] = question
            
            # Save choices for each question
            for prefix, question in question_mapping.items():
                choice_formset_prefix = f'choices-{prefix}'

                ChoiceFormset = ChoiceInlineFormset(
                    request.POST,
                    instance=question,
                    prefix=choice_formset_prefix
                )

                if ChoiceFormset.is_valid():
                    choices = ChoiceFormset.save(commit=False)
                    for choice in choices:
                        if choice.choices_text.strip():  # Ensure non-empty choices
                            choice.question = question
                            choice.save()

            return redirect('edit_survey', survey_id=survey.id)
            
    # Initialize choice formsets for rendering
    choice_formsets = {}
    for i, question_form in enumerate(question_formset):
        question = question_form.instance
        ChoiceFormset = ChoiceInlineFormset(
            instance=question,
            prefix=f'choices-form-{i}'
        )
        choice_formsets[question.pk or f'form-{i}'] = ChoiceFormset

    return render(request, 'insert_question.html', {
        'survey_form': survey_form,
        'question_formset': question_formset,
        'choice_formsets': choice_formsets,
        'is_edit_survey': is_edit_survey,
    })


def answer_survey(request, survey_id=None):
    survey = get_object_or_404(Survey, id=survey_id)
    list_question = Question.objects.filter(survey=survey)

    if request.method == 'POST':
        form = FormToAnswerSurvey(list_question, request.POST)
        if form.is_valid():
            # Create a new SurveyResponse for the user
            survey_response = SurveyResponse.objects.create(
                survey=survey,
                # user=request.user,  # Assuming the user is logged in
                status='submitted'
            )

            # Save the responses to the database
            for key, value in form.cleaned_data.items():
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)

                # Check if it's a multiple choice question
                if isinstance(value, list):  # Multiple choices, list of selected choices
                    for choice_id in value:
                        choice = ResponseChoice.objects.get(id=choice_id)
                        Response.objects.create(
                            user=request.user,
                            survey_response=survey_response,
                            question=question,
                            answer=choice.choices_text
                        )
                else:  # Single choice or text input
                    Response.objects.create(
                        user=request.user,
                        survey_response=survey_response,
                        question=question,
                        answer=value
                    )

            return redirect ('home')
    else:
        form = FormToAnswerSurvey(list_question)

    return render(request, 'answer_survey.html', {
        'survey': survey,
        'form': form,
    })
