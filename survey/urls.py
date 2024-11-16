from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Syukri
    path('my_survey', views.crud_survey, name='crud_survey')
]