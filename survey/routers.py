from rest_framework import routers

from .viewsets import surveyViewSet

router = routers.SimpleRouter()

router.register(r'survey', surveyViewSet, basename="survey")

urlpatterns = router.urls