from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.forms import modelformset_factory
from django.db.models import Prefetch, Max
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetForm

from .models import Survey, Question, QuestionType, SurveyResponse, Response, ResponseChoice, UserProfile, RecommendedSurvey

from .forms import FormToCreateSurvey, FormToCreateQuestion, ChoiceInlineFormset, FormToAnswerSurvey, FormToPublishSurvey, ProfileUpdateForm
import csv

def prevent_logged_in_access(get_response):
    def middleware(request):
        if request.path == '/login/' and request.user.is_authenticated:
            return redirect('home')
        response = get_response(request)
        return response
    return middleware

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('/admin/')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Username atau password salah.")
        else:
            messages.error(request, "Form tidak valid.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

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
            
            # selain membuat user, buat juga profile untuk user
            user_profile = UserProfile.objects.create(user = user, respoint = 50)
            user_profile.save()

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

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def list_my_survey(request):
    list_semua = Survey.objects.filter(user=request.user)
    return render(request, 'my_survey.html', {'surveys': list_semua, 'user': request.user})

def list_survey_fyp(request):
    surveys = Survey.objects.filter(status=True).prefetch_related('recommended_surveys')
    list_my = Survey.objects.filter(user=request.user)
    list_fyp = surveys.exclude(id__in=list_my.values_list('id', flat=True))

    recommended_surveys = RecommendedSurvey.objects.all()
    context = {
        'surveys': list_fyp,
        'recommended_surveys': recommended_surveys,
    }
    return render(request, 'fyp.html', context)

@login_required
def export_responses_to_csv(request, survey_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'

    writer = csv.writer(response)

    survey = get_object_or_404(Survey, id=survey_id)
    questions = Question.objects.filter(survey=survey).order_by('id')
    survey_response = get_object_or_404(SurveyResponse, survey=survey)

    question_texts = [question.question_text for question in questions]
    writer.writerow(question_texts)

    row =[]
    responses = Response.objects.filter(survey_response=survey_response).order_by('user')
    print(len(questions))
    i=0
    for question_response in responses:
        if i != len(questions):
            i+=1
            row.append(question_response.answer)
        else:
            writer.writerow(row)
            row = [question_response.answer]
            i=1
    writer.writerow(row)

    return response

@login_required
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        survey_name = survey.title
        survey.delete()
        messages.warning(request, f"Survey '{survey_name}' has been successfully deleted")
    else:
        messages.error(request, "Invalid request. Surveys can only be deleted through POST requests")
    return redirect('list_my_survey')

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST' or 'GET':
        survey = question.survey
        question.delete()
        return redirect('edit_survey', survey_id=survey.id)
    else:
        return redirect('edit_survey', survey_id=question.survey.id)

@login_required
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
        # kalau survey belum ada, buat dulu yang baru sesuai dengan form
        # jangan lupa surveynya disave dulu
        if survey_form.is_valid() and question_formset.is_valid():
            # Save survey first to generate survey_id
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()

        publishData = RecommendedSurvey.objects.filter(survey=survey).first()    
        if not publishData:
            publishData = RecommendedSurvey.objects.create(
                survey=survey,
                token_debit=0,
                limit=0
            )

        if survey_form.is_valid() and question_formset.is_valid():
            survey = survey_form.save(commit=False)
            survey.user = request.user
            total_price = 0
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

                        question_type = get_object_or_404(QuestionType, name=question.question_type)
                        total_price += question_type.price
                    
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

            survey.total_price = total_price
            survey.save()
            return redirect('list_my_survey')

    choice_formsets = {}
    for i, question_form in enumerate(question_formset):
        question = question_form.instance
        ChoiceFormset = ChoiceInlineFormset(
            instance=question,
            prefix=f'choices-form-{i}'
        )
        choice_formsets[question.pk or f'form-{i}'] = ChoiceFormset

    return render(request, 'create_survey.html', {
        'survey_form': survey_form,
        'question_formset': question_formset,
        'choice_formsets': choice_formsets,
        'is_edit_survey': is_edit_survey,
    })

def answer_survey(request, survey_id=None):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = Question.objects.filter(survey=survey)
    survey_response = SurveyResponse.objects.filter(survey=survey).first()    

    if request.method == 'POST':
        form = FormToAnswerSurvey(questions, request.POST)

        if form.is_valid():

            if survey_response:
                survey_response.status = 'submitted'
                survey_response.save()
            else :
                survey_response = SurveyResponse.objects.create(
                    survey=survey,
                    status='submitted'
                )

            for key, value in form.cleaned_data.items():
                question_id = key.split('_')[1]
                question = get_object_or_404(Question, id=question_id)

                choice = ResponseChoice.objects.filter(question=question_id)
                print(question_id)
                print(choice)
                if not choice:
                    Response.objects.create(
                        survey_response=survey_response,
                        question=question,
                        answer=value,
                        user=request.user
                    )
                else:  # Multiple-choice response
                    Response.objects.create(
                        survey_response=survey_response,
                        question=question,
                        answer=ResponseChoice.objects.get(id=value),
                        user=request.user
                    )

            token_debit = RecommendedSurvey.objects.get(survey=survey)
            token_debit.token_debit -= survey.total_price
            token_debit.save()

            surveyor_profile = UserProfile.objects.get(user=survey.user) 
            surveyor_profile.respoint -= survey.total_price
            surveyor_profile.save()

            user_profile = UserProfile.objects.get(user=request.user) 
            user_profile.respoint += survey.total_price
            user_profile.save()
            return redirect('home')
    else:
        form = FormToAnswerSurvey(questions)

    if not Response.objects.filter(user=request.user, survey_response=survey_response):
        isResponded = False
    else:
        isResponded = True
        

    return render(request, 'answer_survey.html', {
        'survey': survey,
        'form': form,
        'isResponded' : isResponded,
    })

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None  # If the user does not have a profile

    context = {
        'user': user,
        'profile': profile,
    }

    return render(request, 'profile.html', context)

def update_profile(request):
    user = request.user
    try:
        # Retrieve the existing profile
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create a new profile if one does not exist
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        print(request.POST)
        if form.is_valid():
            # Update the user's full name if provided
            full_name = form.cleaned_data.get('full_name', '')
            if full_name:
                user.first_name, user.last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')
                user.save()

            # Save the UserProfile instance
            form.save()
            return redirect('profile')  # Redirect after successful update
        else:
            print('form invalid')
    else:
        form = ProfileUpdateForm(instance=profile)

    # Render the form with the profile instance
    return render(request, 'update_profile.html', {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')  # Arahkan ke halaman profil setelah berhasil
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

@login_required
def publish_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == 'POST':
        form = FormToPublishSurvey(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = FormToPublishSurvey(instance=survey)

    return render(request, 'publish_survey.html', {
        'form': form,
        'survey': survey,
    })
