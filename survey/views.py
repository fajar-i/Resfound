from django.shortcuts import render
# Syukri
from .models import Survey

def home(request):
    return render(request, 'home.html')

# Syukri
def crud_survey(request):
    return render(request, 'crud_survey.html')

def list_my_survey(request):
    list_semua = Survey.objects.all()
    return render(request, 'crud_survey.html', {'surveys': surveys})