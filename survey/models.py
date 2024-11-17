from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    id = models.CharField(primary_key=True, max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    opening_time = models.DateTimeField(null=True, blank=True)
    closing_time = models.DateTimeField(null=True, blank=True)
    total_price = models.IntegerField(default=0)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.CharField(primary_key=True, max_length=255, unique=True)
    question_text = models.TextField(max_length=1000)
    question_type = models.CharField(max_length=255)
    img = models.BinaryField(null=True, blank=True, editable=True)

    def __str__(self):
        return self.question_text


class QuestionOrder(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='question_orders')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_orders')
    order = models.IntegerField()

    class Meta:
        unique_together = ('survey', 'question', 'order')

    def __str__(self):
        return f"Order {self.order} in Survey {self.survey}"


class QuestionType(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.name


class ResponseChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    id = models.CharField(primary_key=True, max_length=255, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"Response to Survey {self.survey}"


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Response by {self.user} to {self.question}"


class RecommendedSurvey(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='recommendations')
    token_debit = models.IntegerField()
    limit = models.IntegerField()

    def __str__(self):
        return f"Recommendation for Survey {self.survey}"
