from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch, Max
from django.urls import reverse

# Syukri
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


def Insert_Question(request, survey_id):
    survey = Survey.objects.get(pk=survey_id)  # Get the specific survey instance

    if request.method == 'POST':
        # questionsForm adalah variabel yang ada di forms.py
        formset = questionsForm(request.POST, request.FILES, queryset=survey.questions.all())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.survey = survey  # Assign the survey to the question
                instance.save()
            formset.save_m2m()  # Save many-to-many relationships, if any
            return redirect('Insert_Question', survey_id=survey.id)
        else:
            print("Formset Errors:", formset.errors)
    else:
        formset = questionsForm(queryset=survey.questions.all())

    return render(request, 'Insert_Question.html', {'formset': formset, 'survey': survey})
