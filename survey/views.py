from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch, Max
from django.urls import reverse
from django.forms import modelformset_factory

from .models import Survey, Question, QuestionType, ResponseChoice
from .forms import FormToCreateSurvey, FormToCreateQuestion, ChoiceInlineFormset

def home(request):
    return render(request, 'home.html')

def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'my_survey.html', {'surveys': list_semua})

def answer_survey(request, survey_id=None):
    survey = get_object_or_404(Survey, id=survey_id)
    list_question = Question.objects.filter(survey=survey)
    
    return render(request, 'answer_survey.html', {
        'survey': survey,
        'questions': list_question
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
        extra=extra_forms
    )

    question_formset = QuestionFormSet(
        request.POST or None,
        request.FILES or None,
        queryset=survey.questions.all() if survey else Question.objects.none()
    )

    if request.method == 'POST':
        # Handle form submission
        if survey_form.is_valid() and question_formset.is_valid():
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()

            for question_form in question_formset:
                if question_form.is_valid():
                    question = question_form.save(commit=False)
                    if not question.question_type_id:
                        question.question_type_id = 1
                    if question.question_text:
                        question.survey = survey
                        question.save()
                    # Process choices for this question
                    ChoiceFormset = ChoiceInlineFormset(
                        request.POST,
                        instance=question,
                        prefix=f'choices-{question_form.prefix}',
                    )
                    if ChoiceFormset.is_valid():
                        choices = ChoiceFormset.save(commit=False)
                        for choice in choices:
                            choice.question = question
                            choice.save()

            return redirect('edit_survey', survey_id=survey.id)

    # Initialize choice formsets for rendering
    choice_formsets = {}
    for question_form in question_formset:
        question = question_form.instance
        ChoiceFormset = ChoiceInlineFormset(
            instance=question,
            prefix=f'choices-{question_form.prefix}'
        )
        choice_formsets[question.pk or question_form.prefix] = ChoiceFormset

    return render(request, 'insert_question.html', {
        'survey_form': survey_form,
        'question_formset': question_formset,
        'choice_formsets': choice_formsets,
        'is_edit_survey': is_edit_survey,
    })

def answer_survey(request, survey_id=None):
    survey = get_object_or_404(Survey, id=survey_id)
    list_question = Question.objects.filter(survey=survey)
    for_html = {
        'survey': survey,
        'questions': list_question
    }
    return render(request, 'answer_survey.html', for_html)
    