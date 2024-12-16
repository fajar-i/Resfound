from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import UserProfile, Survey, RecommendedSurvey, Question, ResponseChoice
from .serializers import SurveySerializer, PublishSerializer, ProfileSerializer, ResponseChoiceSerializer, QuestionSerializer

class ProfileViewSets(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    
class SurveyViewSets(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [AllowAny]

class PublishViewSets(viewsets.ModelViewSet):
    queryset = RecommendedSurvey.objects.all()
    serializer_class = PublishSerializer
    permission_classes = [AllowAny]

class ChoiceViewSets(viewsets.ModelViewSet):
    queryset = ResponseChoice.objects.all()
    serializer_class = ResponseChoiceSerializer
    permission_classes = [AllowAny]

class QuestionViewSets(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

