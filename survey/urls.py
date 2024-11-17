from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Syukri
    path('list_my_survey/', views.list_my_survey, name='list_my_survey'),

    path('create_survey/', views.create_or_edit_survey, name='create_survey'),
    path('edit_survey/<int:survey_id>/', views.create_or_edit_survey, name='edit_survey')

    
]