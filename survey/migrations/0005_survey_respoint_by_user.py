# Generated by Django 5.1.4 on 2024-12-15 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_alter_question_img_alter_survey_user_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='respoint_by_user',
            field=models.IntegerField(default=0),
        ),
    ]
