from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # Hanya perlu diimpor sekali
from rest_framework import routers
from survey.viewsets import SurveyViewSets  # Import your viewsets

router = routers.SimpleRouter()
router.register(r'survey', SurveyViewSets, basename='survey')  # Register the viewset

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Mengarahkan root URL ke /login/
    path('survey/', include('survey.urls')),  # Pastikan survey.urls sudah benar
    path('api/', include((router.urls, 'core_api'), namespace='core_api')),
]
