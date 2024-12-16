from rest_framework import serializers
from .models import Survey, SurveyResponse, Response, ResponseChoice, Question, RecommendedSurvey, UserProfile

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

class PublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedSurvey
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['respoint']
        
class ResponseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseChoice
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

