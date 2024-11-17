from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# Syukri
from .models import Survey, Question, QuestionType
from .forms import FormToCreateSurvey, FormToAddQuestion


def home(request):
    from .urls import urlpatterns  # Lazy import
    return render(request, 'home.html', {'urlpatterns': urlpatterns})


# Syukri
def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'my_survey.html', {'surveys': list_semua})

def create_or_edit_survey(request, survey_id=None):
    if survey_id:
        survey = get_object_or_404(Survey, id=survey_id, user=request.user)
    else:
        survey = None

    if request.method == 'POST' and 'survey_form' in request.POST:
        survey_form = FormToCreateSurvey(request.POST, instance=survey)
        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()
            messages.success(request, f"Survey {'updated' if survey_id else 'created'} successfully!")
            return redirect('edit_survey', survey_id=survey.id)
    else:
        survey_form = FormToCreateSurvey(instance=survey)

    question_form = FormToAddQuestion()

    if request.method == 'POST' and 'question_form' in request.POST:
        question_form = FormToAddQuestion(request.POST, request.FILES)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.survey = survey
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('edit_survey', survey_id=survey.id)

    questions = Question.objects.filter(survey=survey).order_by('question_order') if survey else None

    context = {
        'form': survey_form,
        'is_edit': bool(survey_id),
        'question_form': question_form,
        'questions': questions,
    }
    return render(request, 'create_survey.html', context)