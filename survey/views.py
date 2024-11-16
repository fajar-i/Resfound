from django.shortcuts import render
# Syukri
from .models import Survey
from .forms import FormToCreateSurvey

def home(request):
    return render(request, 'home.html')

# Syukri
def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'crud_survey.html', {'surveys': surveys})

def my_survey(request):
    return render(request, 'crud_survey.html')

def create_survey(request):
    if request.method == 'POST':
        form = FormToCreateSurvey(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = request.user  # Assuming the user is logged in
            survey.save()
            return redirect('crud_survey')  # Replace with the name of your survey list page
    else:
        form = FormToCreateSurvey()
    
    return render(request, 'create_survey.html', {'form': form})
