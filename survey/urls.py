from django.contrib import admin
from django.urls import path, include
from . import views
from .views import login_view, home_view, register_view, logout_view
from django.contrib.auth import views as auth_views  # Untuk menggunakan views dari django auth

urlpatterns = [
    # Arahkan root URL ke login
    path('', login_view, name='login'),  # Halaman utama diarahkan ke login
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # URL dari aplikasi survei
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('list_my_survey/', views.list_my_survey, name='list_my_survey'),
    path('fyp/', views.list_my_survey, name='fyp'),
    path('create_survey/', views.create_survey, name='create_survey'),
    path('edit_survey/<int:survey_id>/', views.create_survey, name='edit_survey'),  # Ganti ke edit_survey jika perlu
    path('delete_survey/<int:survey_id>/', views.delete_survey, name='delete_survey'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('answer_survey/<int:survey_id>/', views.answer_survey, name='answer_survey'),

    path('home/', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),  # Tambahkan logout path
    
    
    # Reset Password URL patterns
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Halaman Settings
    path('settings/', views.settings_view, name='settings'),
    path('settings/add-questionnaire/', views.add_questionnaire_view, name='add_questionnaire'),
    path('settings/change-password/', views.change_password_view, name='change_password'),
]
