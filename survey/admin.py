from django.contrib import admin
from .models import Survey, Question, Response, SurveyResponse, RecommendedSurvey, QuestionType, ResponseChoice,UserProfile

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(QuestionType)
admin.site.register(SurveyResponse)
admin.site.register(Response)
admin.site.register(RecommendedSurvey)
admin.site.register(ResponseChoice)
admin.site.register(UserProfile)