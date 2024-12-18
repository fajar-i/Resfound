from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    respoint = models.IntegerField(default=0)
    picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Enter a valid phone number. Format: +123456789 or 123456789.'
        )]
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
        
class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pemilik_survey')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    opening_time = models.DateTimeField(default=now, null=True, blank=True)
    closing_time = models.DateTimeField(null=True, blank=True)
    total_price = models.IntegerField(default=0)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class QuestionType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Question(models.Model):
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(max_length=1000)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='questions')
    question_order = models.IntegerField()
    img = models.ImageField(upload_to='images/', null=True, blank=True, editable=True)

    class Meta:
        unique_together = ('survey', 'question_order')
        indexes = [
            models.Index(fields=['survey', 'question_order']),
        ]

    def __str__(self):
        return self.question_text

class ResponseChoice(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choices_text = models.TextField(max_length=1000)

    def __str__(self):
        return self.choices_text

class SurveyResponse(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ]
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"Response to Survey {self.survey}"

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField(max_length=1000)

    def __str__(self):
        return f"Response by {self.user} to {self.question}"

class RecommendedSurvey(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='recommended_surveys')
    token_debit = models.PositiveIntegerField()
    limit = models.PositiveIntegerField()

    def __str__(self):
        return f"Recommendation for Survey {self.survey}"
