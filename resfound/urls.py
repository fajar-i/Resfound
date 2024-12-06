from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect # Hanya perlu diimpor sekali

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Mengarahkan root URL ke /login/
    path('survey/', include('survey.urls')),  # Pastikan survey.urls sudah benar
]
