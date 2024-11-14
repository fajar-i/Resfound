from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('survey_baru', views.survey_baru, name='survey_baru'),
]