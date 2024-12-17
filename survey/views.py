from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.forms import modelformset_factory
from django.db.models import Prefetch, Max, F, Q, OuterRef, Subquery
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
                    email_template_name='registration/password_reset_email.html',
                )
                messages.success(request, "Link untuk reset password telah dikirim ke email Anda.")
                return redirect("login") 
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

from django.utils.timezone import now

@login_required
def list_survey_fyp(request):
    # Get the current time
    current_time = now()

    # Fetch surveys that are active and within the opening and closing time
    

    # Subquery to compute the maximum token_debit and limit for each survey
    recommended_surveys = RecommendedSurvey.objects.filter(
        survey=OuterRef('pk')
    ).annotate(
        min_required_token=F('survey__total_price')
    ).values('token_debit', 'min_required_token')

    # Fetch surveys with proper filters
    surveys = Survey.objects.filter(
        status=True,
        opening_time__lte=current_time,
        closing_time__gte=current_time
    ).annotate(
        max_token_debit=Subquery(recommended_surveys.values('token_debit')[:1]),
        min_required_token=Subquery(recommended_surveys.values('min_required_token')[:1]),
    ).filter(
        Q(max_token_debit__gt=F('min_required_token'))
    ).order_by('-max_token_debit')



    # Surveys the user has already responded to
    responded_surveys = SurveyResponse.objects.filter(
        responses__user=request.user,
    ).values_list('survey_id', flat=True)

    # Recommended surveys logic
    # recommended_surveys = RecommendedSurvey.objects.all().order_by('-token_debit')
    # diurutkan descending debit token
    
    limited_survey_ids = RecommendedSurvey.objects.filter(
        limit__gt=0  # Only include surveys with a limit greater than 0
    ).values_list('survey_id', flat=True)

    # Apply the limit filter to surveys
    surveys = surveys.filter(id__in=limited_survey_ids)
    
    all_surveys = Survey.objects.all()
    closed_surveys = all_surveys.exclude(id__in=surveys.values_list('id', flat=True))

    # daripada exclude survey milik sendiri, kita buat saja survey milik kita terlihat di fyp
    # tapi nanti di html dibuat tombolnya tidak bisa "answer survey"
    # my_survey = Survey.objects.filter(user = request.user)
    # surveys = surveys.exclude(id__in=my_survey.values_list('id', flat=True))
    # closed_surveys = closed_surveys.exclude(id__in=my_survey.values_list('id', flat=True))

    # Context for the template
    context = {
        'surveys': surveys,
        'closed_surveys': closed_surveys,
        'recommended_surveys': recommended_surveys,
        'responded_survey_ids': list(responded_surveys),  # Pass list of IDs to template
        'user': request.user, #untuk mengetahui ini survey milik siapa
        'current_time': current_time, #supaya survey yang belum buka tombolnya bisa di disabled
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
        if survey_form.is_valid() and question_formset.is_valid():
            survey = survey_form.save(commit=False)
            survey.user = request.user
            survey.save()
            total_price = 0

            publishData = RecommendedSurvey.objects.filter(survey=survey).first()    
            if not publishData:
                publishData = RecommendedSurvey.objects.create(
                    survey=survey,
                    token_debit=0,
                    limit=0
                )

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
                    
                    # Delete choices marked for deletion in the formset
                    for choice in ChoiceFormset.deleted_objects:
                        choice.delete()

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
                else: 
                    Response.objects.create(
                        survey_response=survey_response,
                        question=question,
                        answer=ResponseChoice.objects.get(id=value),
                        user=request.user
                    )

            token_debit = RecommendedSurvey.objects.get(survey=survey)
            token_debit.token_debit -= survey.total_price
            token_debit.save()

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
        profile = None 

    context = {
        'user': user,
        'profile': profile,
    }

    return render(request, 'profile.html', context)

def update_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        print(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name', '')
            if full_name:
                user.first_name, user.last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')
                user.save()

            form.save()
            return redirect('profile')
        else:
            print('form invalid')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')  
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
