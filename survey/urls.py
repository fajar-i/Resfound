from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Syukri
    path('my_survey', views.my_survey, name='my_survey'),
    path('create_survey', views.create_survey, name='create_survey'),
    path('list_my_survey', views.list_my_survey, name='list_my_survey'),
    path('view_question', views.create_question, name='create_question')
]