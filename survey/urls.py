from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Untuk menggunakan views dari django auth
from . import views
from .views import login_view, home_view, register_view, logout_view

urlpatterns = [
    # Arahkan root URL ke login
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),

    # URL dari aplikasi survei
    path('fyp/', views.list_survey_fyp, name='fyp'),
    path('create_survey/', views.create_survey, name='create_survey'),
    path('list_my_survey/', views.list_my_survey, name='list_my_survey'),
    path('edit_survey/<int:survey_id>/', views.create_survey, name='edit_survey'),  # Ganti ke edit_survey jika perlu
    path('delete_survey/<int:survey_id>/', views.delete_survey, name='delete_survey'),
    path('answer_survey/<int:survey_id>/', views.answer_survey, name='answer_survey'),
    path('publish_survey/<int:survey_id>/', views.publish_survey, name='publish_survey'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('delete_choice/<int:question_id>/', views.delete_question, name='delete_question'),
    path('export_responses_to_csv/<int:survey_id>/', views.export_responses_to_csv, name='export_responses_to_csv'),

    #login
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('logout/', logout_view, name='logout'),  # Tambahkan logout path
    path('update_profile/', views.update_profile, name='update_profile'),
    
    # Reset Password URL patterns
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Halaman Settings
    path('settings/', views.change_password_view, name='settings'),
    path('settings/change-password/', views.change_password_view, name='change_password'),
]
