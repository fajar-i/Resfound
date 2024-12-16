from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from survey.viewsets import ProfileViewSets, SurveyViewSets, PublishViewSets, ChoiceViewSets, QuestionViewSets

router = routers.SimpleRouter()
router.register(r'profile', ProfileViewSets, basename="profile")
router.register(r'survey', SurveyViewSets, basename='survey')
router.register(r'question', QuestionViewSets, basename='question')
router.register(r'choice', ChoiceViewSets, basename='choice')
router.register(r'publish', PublishViewSets, basename="publish")

urlpatterns = [
    path('', include('survey.urls')),
    path('api/', include((router.urls, 'core_api'), namespace='core_api')),
    path('admin/', admin.site.urls),
    # path('login/', lambda request: redirect('login')),  # Mengarahkan root URL ke /login/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)