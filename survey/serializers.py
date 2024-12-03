from rest_framework import serializers
from .models import Survey, Question, QuestionType, ResponseChoice, SurveyResponse, Response

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'