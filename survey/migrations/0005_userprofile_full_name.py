# Generated by Django 5.1.3 on 2024-12-15 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_alter_userprofile_id_alter_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='full_name',
            field=models.CharField(default='sku', max_length=255),
            preserve_default=False,
        ),
    ]
