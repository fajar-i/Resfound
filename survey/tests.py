from django.test import TestCase
from django.contrib.auth.models import User
from .models import Survey, Question, QuestionOrder, SurveyResponse, Response

class SurveyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.survey = Survey.objects.create(id="survey1", user=self.user, title="Test Survey")
        self.question = Question.objects.create(id="question1", question_text="Sample question?", question_type="text")
        self.survey_response = SurveyResponse.objects.create(survey=self.survey, id="response1", status="complete")
        self.response = Response.objects.create(user=self.user, survey_response=self.survey_response, question=self.question, answer="Sample answer")

    def test_survey_creation(self):
        self.assertEqual(self.survey.user, self.user)
        self.assertEqual(self.survey.title, "Test Survey")

    def test_relationships(self):
        self.assertIn(self.survey_response, self.survey.responses.all())
        self.assertIn(self.response, self.survey_response.responses.all())
        self.assertEqual(self.response.user, self.user)
        self.assertEqual(self.response.question, self.question)
