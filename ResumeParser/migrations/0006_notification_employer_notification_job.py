# Generated by Django 5.0 on 2024-01-02 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ResumeParser', '0005_alter_notification_candidate'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='employer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='job',
            field=models.IntegerField(null=True),
        ),
    ]
