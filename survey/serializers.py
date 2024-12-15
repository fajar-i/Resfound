from rest_framework import serializers
from .models import Survey, SurveyResponse, Response, ResponseChoice, Question, RecommendedSurvey

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

class PublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedSurvey
        fields = '__all__'
        

class ResponseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseChoice
        fields = ['id', 'choices_text']

class ResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'question_text', 'answer']

class SurveyResponseSerializer(serializers.ModelSerializer):
    responses = ResponseSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = ['id', 'status', 'last_updated', 'responses']

class QuestionSerializer(serializers.ModelSerializer):
    question_type = serializers.StringRelatedField()  # Returns the name of the QuestionType
    choices = ResponseChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'question_order', 'img', 'choices']

class SurveySerializer_Syukri(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    responses = SurveyResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'creation_date', 'opening_time', 
                  'closing_time', 'total_price', 'status', 'questions', 'responses']

