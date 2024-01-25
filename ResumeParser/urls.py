from django.urls import path
from .views import *
urlpatterns = [
    path('',guest,name='guest'),
    path('Home/',home,name='home'),
    path('Employer_Home/',emp_home,name='emp_home'),
    path('SignUp/',register, name='candidate_register'),
    path('Employer_SignUp/',employee_register, name='employer_register'),
    path('SignIn/',signin, name='login'),
    path('Employer_SignIn/',emp_login, name='emp_login'),
    path('SignOut/',signout, name='log_out'),
    path('job-details/',job_details, name='job_details'),
    path('job-posting/',job_posting, name='job_posting'),
    # path('delete_job/',delete_job, name='delete_job'),
    path('all-jobs/',all_jobs, name='all_jobs'),
    path('browse-jobs/',browse_jobs, name='browse-jobs'),
    path('resume-upload/',resume_upload, name='resume-upload'),
    path('manage-resume/',manage_resume, name='manage-resume'),
    path('selected-candidate/',selected_candidate, name='selected-candidate'),
    path('delete-candidate/',delete_candidate, name='delete-candidate'),
    path('Notification/',notify, name='notify'),
    path('view-notify/',view_notification, name='view-notify'),
    path('delete-notify/',delete_notification, name='delete-notify'),
]