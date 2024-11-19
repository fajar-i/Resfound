from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Insert_Question/<int:survey_id>/', views.Insert_Question, name='Insert_Question'),
    # Syukri
    path('list_my_survey/', views.list_my_survey, name='list_my_survey'),
    path('create_survey/', views.create_or_edit_survey, name='create_survey'),
    path('edit_survey/<int:survey_id>/', views.create_or_edit_survey, name='edit_survey'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question')

]