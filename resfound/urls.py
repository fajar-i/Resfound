from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from survey.viewsets import SurveyViewSets, PublishViewSets

router = routers.SimpleRouter()
router.register(r'survey', SurveyViewSets, basename='survey')
router.register(r'publish', PublishViewSets, basename="publish")

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/', lambda request: redirect('login')),  # Mengarahkan root URL ke /login/
    path('', include('survey.urls')),
    path('api/', include((router.urls, 'core_api'), namespace='core_api')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)