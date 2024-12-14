from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # Hanya perlu diimpor sekali
from rest_framework import routers
from survey.viewsets import SurveyViewSets  # Import your viewsets
from django.conf import settings
from django.conf.urls.static import static

router = routers.SimpleRouter()
router.register(r'survey', SurveyViewSets, basename='survey')  # Register the viewset

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/', lambda request: redirect('login')),  # Mengarahkan root URL ke /login/
    path('', include('survey.urls')),  # Pastikan survey.urls sudah benar
    path('api/', include((router.urls, 'core_api'), namespace='core_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)