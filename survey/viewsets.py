from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Survey, SurveyResponse, RecommendedSurvey, Response as ResponseModel
from .serializers import SurveySerializer, PublishSerializer, SurveyResponseSerializer, ResponseSerializer

class SurveyViewSets(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [AllowAny]

class PublishViewSets(viewsets.ModelViewSet):
    queryset = RecommendedSurvey.objects.all()
    serializer_class = PublishSerializer
    permission_classes = [AllowAny]



class SurveyResponsesAPIView(APIView):
    def get(self, request, survey_id):
        # Fetch the survey or return a 404 if not found
        survey = get_object_or_404(Survey, id=survey_id)
        
        # Prefetch related data for efficiency
        survey_responses = SurveyResponse.objects.filter(survey=survey).prefetch_related(
            'responses__question'
        )

        # Prepare the response data
        data = []
        for response in survey_responses:
            answers = [
                {
                    'question_text': answer.question.question_text,
                    'answer': answer.answer
                }
                for answer in response.responses.all()
            ]
            data.append({
                'respondent_id': response.id,
                'status': response.status,
                'last_updated': response.last_updated,
                'answers': answers,
            })

        # Return survey details along with all responses
        return Response({
            'survey': SurveySerializer(survey).data,
            'responses': data,
        })
