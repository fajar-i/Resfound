from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch, Max
from django.urls import reverse

from .models import Survey, Question, QuestionType, ResponseChoice
from .forms import FormToCreateSurvey, FormToCreateQuestion, FormToCreateChoices, questionsForm

def home(request):
    return render(request, 'home.html')

# Syukri
def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'my_survey.html', {'surveys': list_semua})

def create_or_edit_survey(request, survey_id=None):
    if survey_id:
        survey = Survey.objects.get(pk=survey_id)
        questions = Question.objects.filter(survey=survey).order_by('question_order')
        survey_form = FormToCreateSurvey(instance=survey)
    else:
        survey = None
        questions = None
        survey_form = FormToCreateSurvey()

    is_edit_survey = bool(survey)

    if request.method == 'POST':
        if 'survey_form' in request.POST:
            survey_form = FormToCreateSurvey(request.POST, instance=survey)
            if survey_form.is_valid():
                survey = survey_form.save(commit=False)
                survey.user = request.user
                survey.save()
                return redirect('list_my_survey')
            # else:
                # form tidak valid, error
        if 'question_form' in request.POST:
            question_id = request.POST.get('question-id')
            if question_id:
                question = Question.objects.get(pk=int(question_id), survey=survey)
                question_form = FormToCreateQuestion(request.POST, instance=question)
            else:
                question_form = FormToCreateQuestion(request.POST)
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.survey = survey
                question.save()
                return redirect('edit_survey', survey_id=survey.id)
            # else:
            #     form tidak valid, error
        else:
            survey = Survey.objects.get(pk=survey_id)
            is_edit_survey = bool(survey)
            question_form = FormToCreateQuestion()
            if survey:
                survey_form = FormToCreateSurvey(instance=survey)
                questions = Question.objects.filter(survey=survey).order_by('question_order')
            else:
                survey_form = FormToCreateSurvey()
                questions = None
            return render(request, 'create_survey.html', {
                # list semua "variabel" yang dibutuhkan oleh file html
                'is_edit_survey': is_edit_survey,
                'survey_form': survey_form,
                'question_form': question_form,
                'questions': questions
            })
    
    is_edit_survey = bool(survey)
    question_form = FormToCreateQuestion()
    if survey:
        survey_form = FormToCreateSurvey(instance=survey)
        questions = Question.objects.filter(survey=survey).order_by('question_order')
    else:
        survey_form = FormToCreateSurvey()
        questions = None
    return render(request, 'create_survey.html', {
        # list semua "variabel" yang dibutuhkan oleh file html
        'is_edit_survey': is_edit_survey,
        'survey_form': survey_form,
        'question_form': question_form,
        'questions': questions
    })

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
        return redirect('Insert_Question', survey_id=survey.id)
    else:
        return redirect('Insert_Question', survey_id=question.survey.id)

def Insert_Question(request, survey_id=None):
    # Get survey instance if editing; otherwise, None for creating
    survey = get_object_or_404(Survey, pk=survey_id) if survey_id else None
    is_edit_survey = survey is not None

    # Initialize forms
    survey_form = FormToCreateSurvey(request.POST or None, instance=survey)
    question_formset = questionsForm(
        request.POST or None,
        request.FILES or None,
        queryset=survey.questions.all() if survey else Survey.objects.none()
    )

    if request.method == 'POST':
        # Handle both forms' submission
        if survey_form.is_valid() and question_formset.is_valid():
            # Save survey
            survey = survey_form.save(commit=False)
            survey.user = request.user  # Ensure the user is assigned
            survey.save()

            # Save associated questions
            question_instances = question_formset.save(commit=False)
            for question in question_instances:
                question.survey = survey  # Link questions to the survey
                question.save()
            question_formset.save_m2m()

            # Redirect to the same page or another appropriate view
            return redirect('Insert_Question', survey_id=survey.id)

    # Render template
    return render(request, 'insert_question.html', {
        'survey_form': survey_form,
        'question_form': question_formset,
        'survey': survey,
        'is_edit_survey': is_edit_survey,
    })
