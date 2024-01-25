from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    user_type_data = ((1,'employer'),(2,'candidate'))
    user_type = models.CharField(default=1,choices=user_type_data,max_length=10)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions'
    )



class Employer(models.Model):
    company_name = models.CharField(max_length=100)
    logo = models.FileField(null=True)
    desc = models.CharField(max_length=2000)
    mobile = models.CharField(max_length=10)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    objects = models.Manager()



class Candidate(models.Model):
    mobile = models.CharField(max_length=10)
    resume = models.FileField(null=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    objects = models.Manager()


class ResumeData(models.Model):
    candidate_name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    graduation_year = models.IntegerField()
    CGPA = models.FloatField()
    skills = models.CharField(max_length=500)
    exp = models.IntegerField()
    languages = models.CharField(max_length=200)


class Jobs(models.Model):
    job_title = models.CharField(max_length=100)
    job_nature = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    job_description = models.CharField(max_length=1000)
    job_responsibility = models.CharField(max_length=1000)
    job_qualification = models.CharField(max_length=200)
    job_skills = models.CharField(max_length=500)
    job_graduation_year = models.CharField(max_length=100)
    job_CGPA = models.CharField(max_length=20)
    job_exp = models.IntegerField()
    job_salary = models.CharField(max_length=20)
    job_languages = models.CharField(max_length=200)
    published_date = models.DateTimeField(auto_now_add=True)
    last_date = models.DateTimeField()
    company_name = models.ForeignKey(Employer,on_delete=models.CASCADE)




class JobMatch(models.Model):
    candidate_id = models.IntegerField(null=True)
    job_id = models.IntegerField(null=True)
    company_id = models.IntegerField(null=True)
    match_score = models.DecimalField(max_digits=100, decimal_places=2)


class Notification(models.Model):
    candidate = models.IntegerField(null=True)
    employer = models.IntegerField(null=True)
    job = models.IntegerField(null=True)
    message = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        if instance.user_type == 1:
            Employer.objects.create(admin=instance,company_name="",mobile="")
        if instance.user_type == 2:
            Candidate.objects.create(admin=instance,mobile="")



@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type == 1:
        instance.employer.save()
    if instance.user_type == 2:
        instance.candidate.save()
