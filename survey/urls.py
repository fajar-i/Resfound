from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Syukri
    path('my_survey', views.list_my_survey, name='list_my_survey')
]