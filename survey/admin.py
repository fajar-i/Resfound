from django.contrib import admin
from .models import Survey, Question, Response, SurveyResponse, QuestionOrder, RecommendedSurvey, QuestionType, ResponseChoice

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(QuestionOrder)
admin.site.register(QuestionType)
admin.site.register(ResponseChoice)
admin.site.register(SurveyResponse)
admin.site.register(Response)
admin.site.register(RecommendedSurvey)
