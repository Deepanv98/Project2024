# Generated by Django 5.0 on 2023-12-19 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ResumeParser', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobmatch',
            old_name='candidate_name',
            new_name='candidate_id',
        ),
        migrations.AddField(
            model_name='jobmatch',
            name='job_id',
            field=models.IntegerField(null=True),
        ),
    ]