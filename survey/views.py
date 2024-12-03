from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Prefetch, Max
from django.urls import reverse
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .models import Survey, Question, QuestionType, SurveyResponse, Response, ResponseChoice
from .forms import FormToCreateSurvey, FormToCreateQuestion, ChoiceInlineFormset, FormToAnswerSurvey
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,PasswordResetForm

def prevent_logged_in_access(get_response):
    def middleware(request):
        if request.path == '/login/' and request.user.is_authenticated:
            return redirect('home')  # Arahkan pengguna ke home jika sudah login
        response = get_response(request)
        return response
    return middleware


# Akun Pengguna
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Cek apakah user admin atau bukan
                if user.is_staff:  # Jika admin
                    return redirect('/admin/')  # Redirect ke halaman admin
                else:  # Jika user biasa
                    return redirect('home')  # Redirect ke halaman home untuk user
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Form tidak valid.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Password tidak cocok!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan!")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, "Akun berhasil dibuat!")
            return redirect('login')

    return render(request, 'register.html')
    
def reset_password_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='registration/password_reset_email.html',  # Pastikan template ini ada
                )
                # Redirect ke halaman login dengan pesan konfirmasi
                messages.success(request, "Link untuk reset password telah dikirim ke email Anda.")
                return redirect("login")  # Ganti dengan nama URL login Anda
            else:
                form.add_error("email", "Email tidak ditemukan.")
    else:
        form = PasswordResetForm()
    
    return render(request, "reset_password.html", {"form": form})


# Survey
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
        survey = question.survey
        question.delete()
        return redirect('edit_survey', survey_id=survey.id)
    else:
        return redirect('edit_survey', survey_id=question.survey.id)
# survey/views.py
from django.shortcuts import render, get_object_or_404
from .models import Survey
from django.http import HttpResponse

def edit_survey(request, survey_id):
    # Mengambil survey berdasarkan ID
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == "POST":
        # Logika untuk memproses pengeditan survey
        survey.title = request.POST['title']
        survey.description = request.POST['description']
        survey.save()
        return HttpResponse("Survey edited successfully")  # Arahkan ke halaman lain jika perlu
    return render(request, 'survey/edit_survey.html', {'survey': survey})


def create_survey(request, survey_id=None):
    survey = get_object_or_404(Survey, pk=survey_id) if survey_id else None
    is_edit_survey = survey is not None

    survey_form = FormToCreateSurvey(request.POST or None, instance=survey)
    extra_forms = 0 if survey and survey.questions.exists() else 1
    QuestionFormSet = modelformset_factory(Question, form=FormToCreateQuestion, extra=extra_forms)

    question_formset = QuestionFormSet(
        request.POST or None,
        request.FILES or None,
        queryset=survey.questions.all() if survey else Question.objects.none()
    )

    if request.method == 'POST':
        if survey_form.is_valid() and question_formset.is_valid():
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()

            question_mapping = {}
            for i, question_form in enumerate(question_formset):
                if question_form.cleaned_data.get('DELETE'):
                    if question_form.instance.pk:
                        question_form.instance.delete()
                else:
                    question = question_form.save(commit=False)
                    question.survey = survey
                    if question.question_text:
                        question.save()
                        question_mapping[f"form-{i}"] = question

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
                        if choice.choices_text.strip():
                            choice.question = question
                            choice.save()

            return redirect('edit_survey', survey_id=survey.id)

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
            survey_response = SurveyResponse.objects.create(
                survey=survey,
                status='submitted'
            )
            for key, value in form.cleaned_data.items():
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)

                if isinstance(value, list):
                    for choice_id in value:
                        choice = ResponseChoice.objects.get(id=choice_id)
                        Response.objects.create(
                            user=request.user,
                            survey_response=survey_response,
                            question=question,
                            answer=choice.choices_text
                        )
                else:
                    Response.objects.create(
                        user=request.user,
                        survey_response=survey_response,
                        question=question,
                        answer=value
                    )
            return redirect('home')
    else:
        form = FormToAnswerSurvey(list_question)

    return render(request, 'answer_survey.html', {
        'survey': survey,
        'form': form,
    })
