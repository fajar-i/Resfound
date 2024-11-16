from django.shortcuts import render
# Syukri
from .models import Survey

def home(request):
    return render(request, 'home.html')

# Syukri
def list_my_survey(request):
    return render(request, 'crud_survey.html', {'surveys': Survey.objects.all()})