from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Survey
from .serializers import SurveySerializer

class SurveyViewSets(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [AllowAny]

