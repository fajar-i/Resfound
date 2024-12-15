# Generated by Django 5.1.3 on 2024-12-15 16:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$', 'Enter a valid phone number.')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='respoint',
            field=models.IntegerField(default=0),
        ),
    ]
