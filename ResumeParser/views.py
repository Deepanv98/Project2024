from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timezone
from .models import Employer, Jobs, CustomUser, Candidate, JobMatch, Notification
from django.contrib.auth import login
from .UserBackEnd import UserBackEnd
import PyPDF2, os, docx2txt, spacy
from .resumeParser import cleanResume, extract_information_from_resume
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Create your views here.

def guest(request):
    jobs = Jobs.objects.all().order_by('-id')
    candidate_count = Candidate.objects.count()
    employer_count = Employer.objects.count()
    job_count = Jobs.objects.count()
    # print(candidate_count, employer_count)
    current_time = datetime.now(timezone.utc)
    if request.method == 'POST':
        job = request.POST.get('job')
        loc = request.POST.get('loc')
        category = request.POST.get('category')
        print(job, loc, category)

        if Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category).exists():
            jobs = Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category)
        else:
            messages.warning(request, "No Jobs Found")

    for job in jobs:
        print(job.company_name_id)
        emp = Employer.objects.get(id=job.company_name_id)
        # print(emp.logo.url)
        job.logo = emp.logo.url
        time_diff = current_time - job.published_date
        job.time_difference = time_diff.total_seconds()
        job.minutes_ago = int(job.time_difference / 60)  # Calculate minutes ago
        job.hours_ago = int(job.time_difference / 3600)  # Calculate hours ago
        job.days_ago = int(job.time_difference / 86400)  # Calculate days ago
        job.months_ago = int(job.time_difference / (86400 * 30))

    context = {'jobs': jobs, 'c_count': candidate_count, 'e_count': employer_count, 'j_count': job_count}
    return render(request, "guest.html", context)


def home(request):
    jobs = Jobs.objects.all().order_by('-id')
    candidate_count = Candidate.objects.count()
    employer_count = Employer.objects.count()
    job_count = Jobs.objects.count()
    # print(candidate_count, employer_count)
    current_time = datetime.now(timezone.utc)
    if request.method == 'POST':
        job = request.POST.get('job')
        loc = request.POST.get('loc')
        category = request.POST.get('category')
        print(job.lower(),loc,category)
        if Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category).exists():
            print('yes')
            jobs = Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category)
        else:
            messages.warning(request, "No Jobs Found")
            print('no')
    for job in jobs:
        print(job.company_name_id)
        emp = Employer.objects.get(id=job.company_name_id)
        # print(emp.logo.url)
        job.logo = emp.logo.url
        time_diff = current_time - job.published_date
        job.time_difference = time_diff.total_seconds()
        job.minutes_ago = int(job.time_difference / 60)  # Calculate minutes ago
        job.hours_ago = int(job.time_difference / 3600)  # Calculate hours ago
        job.days_ago = int(job.time_difference / 86400)  # Calculate days ago
        job.months_ago = int(job.time_difference / (86400 * 30))

    context = {'jobs': jobs, 'c_count': candidate_count, 'e_count': employer_count, 'j_count': job_count, 'name':request.user.first_name}
    return render(request, 'Home.html', context)

def nav(request):
    print(request.user.first_name)
    return render(request, 'nav.html')

def emp_home(request):
    candidate_count = Candidate.objects.count()
    employer_count = Employer.objects.count()
    job_count = Jobs.objects.count()
    emp = Employer.objects.get(admin_id=request.user.id)
    jobs = Jobs.objects.filter(company_name_id=emp.id).order_by('-id')
    current_time = datetime.now(timezone.utc)
    print(emp.id)

    if request.method == 'POST':
        search = request.POST.get('search')
        print(search)
        if Jobs.objects.filter(company_name_id=emp.id, job_title=search.lower()).exists():
            print('search')
            jobs = Jobs.objects.filter(company_name_id=emp.id, job_title=search.lower())
        elif Jobs.objects.filter(company_name_id=emp.id, category=search).exists():
            jobs = Jobs.objects.filter(company_name_id=emp.id, category=search)
            print('search1')
        else:
            messages.warning(request, "No Jobs")
            print('search2')

    for job in jobs:
        time_diff = current_time - job.published_date
        job.time_difference = time_diff.total_seconds()
        job.minutes_ago = int(job.time_difference / 60)  # Calculate minutes ago
        job.hours_ago = int(job.time_difference / 3600)  # Calculate hours ago
        job.days_ago = int(job.time_difference / 86400)  # Calculate days ago
        job.months_ago = int(job.time_difference / (86400 * 30))

    context = {'logo': emp.logo.url, 'jobs': jobs, 'c_count': candidate_count, 'e_count': employer_count, 'j_count': job_count}
    return render(request, 'emp_home.html', context)


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mob = request.POST.get('mob')
        user = request.POST.get('user')
        pass1 = request.POST.get('pass')
        pass2 = request.POST.get('re_pass')
        print(name, email, mob, user, pass1, pass2)
        if pass1 == pass2:
            if CustomUser.objects.filter(username=user).exists():
                messages.warning(request, 'Username already exist!')
            elif CustomUser.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exist!')
            else:
                cand = CustomUser.objects.create_user(user_type=2, first_name=name, email=email, username=user,
                                                      password=pass1)
                cand.candidate.mobile = mob
                cand.save()
                return redirect(signin)
        else:
            messages.warning(request, 'Password Mismatch!')
    return render(request, "sign_up.html")


def signin(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        pass1 = request.POST.get('pass')
        print(user, pass1)
        candidate = UserBackEnd.authenticate(request, username=user, user_type=2, password=pass1)
        print(candidate)
        if candidate is not None:
            login(request, candidate, backend='ResumeParser.UserBackEnd.UserBackEnd')
            return redirect(home)
        else:
            messages.warning(request, 'Invalid Credentials..')

    return render(request, "sign_in.html")


def signout(request):
    return redirect(guest)


def employee_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        logo = request.FILES['logo']
        desc = request.POST.get('desc')
        cname = request.POST.get('cname')
        email = request.POST.get('email')
        mob = request.POST.get('mob')
        user = request.POST.get('user')
        pass1 = request.POST.get('pass')
        pass2 = request.POST.get('re_pass')
        print(name, cname, email, mob, user, pass1, pass2)
        if pass1 == pass2:
            if CustomUser.objects.filter(username=user).exists():
                messages.warning(request, 'Username already exist!')
            elif CustomUser.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exist!')
            else:
                emp = CustomUser.objects.create_user(user_type=1, first_name=name, email=email, username=user,
                                                     password=pass1)
                emp.employer.company_name = cname
                emp.employer.mobile = mob
                emp.employer.logo = logo
                emp.employer.desc = desc
                emp.save()
                return redirect(emp_login)
        else:
            messages.warning(request, 'Password Mismatch!')
    return render(request, 'emp_signup.html')


def emp_login(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        pass1 = request.POST.get('pass')
        print(user, pass1)
        employer = UserBackEnd.authenticate(request, username=user, user_type=1, password=pass1)
        print(employer)
        if employer is not None:
            login(request, employer, backend='ResumeParser.UserBackEnd.UserBackEnd')
            return redirect(emp_home)
        else:
            messages.warning(request, 'Invalid Credentials..')
    return render(request, 'emp_signin.html')


def job_details(request):
    m = 0
    file = ''
    jid = request.GET.get('jid')
    try:
        if JobMatch.objects.get(candidate_id=request.user.id, job_id=jid):
            m = 1
    except:
        m = 0
    job = Jobs.objects.get(id=jid)
    com = Employer.objects.get(id=job.company_name_id)
    print(request.user.user_type)
    if request.user.user_type == '2':
        res = Candidate.objects.get(admin_id=request.user.id)
        if request.method == 'POST':
            # apply = request.POST.get('apply')
            try:
                file = res.resume.url
            except:
                messages.warning(request, "Please upload Resume!")
            else:
                if file.endswith('.docx'):
                    text = docx2txt.process('C:/Users/usere005/Desktop/CVParser/Resume_Parsing_Project' + file)
                    print(text)
                elif file.endswith('.doc'):
                    # Converting .doc file to .docx
                    docx_file = 'C:/Users/usere005/Desktop/CVParser/Resume_Parsing_Project' + file + 'x'
                    with open(docx_file) as f:
                        text = f.read()
                    os.remove(docx_file)
                    print(text)
                elif file.endswith('.pdf'):
                    with open('C:/Users/usere005/Desktop/CVParser/Resume_Parsing_Project' + file, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                    # print(text)
                else:
                    print('No data')
                cleaned_text = cleanResume(text)
                resume_info = extract_information_from_resume(cleaned_text)

                # Resume information
                resume_skills = set(resume_info.get("Skills", []))
                resume_languages = set(resume_info.get("Languages", []))
                resume_education = set(resume_info.get("Education", []))
                resume_exp = set(resume_info.get("years_of_experience", []))

                # Job information
                job_languages, job_education, job_exp = set(), set(), set()
                job_skills = set(list(job.job_skills.split(',')))
                job_languages.add(job.job_languages)
                job_education.add(job.job_qualification)
                job_exp.add(job.job_exp)

                # Calculate matching sets for skills, languages, and qualifications
                matching_skills = resume_skills & job_skills
                matching_exp = resume_exp & job_exp
                matching_languages = resume_languages & job_languages
                matching_qualifications = resume_education & job_education

                # Calculate the total sets for skills, Experience, languages, and qualifications
                total_resume_set = resume_skills | resume_languages | resume_education | resume_exp
                total_job_set = job_skills | job_languages | job_education | job_exp

                # Calculate similarity scores for each category (skills, languages, qualifications, experience)
                skills_similarity = len(matching_skills) / len(
                    total_resume_set | total_job_set) if total_resume_set | total_job_set else 0
                exp_similarity = len(matching_exp) / len(
                    total_resume_set | total_job_set) if total_resume_set | total_job_set else 0
                languages_similarity = len(matching_languages) / len(
                    total_resume_set | total_job_set) if total_resume_set | total_job_set else 0
                qualifications_similarity = len(matching_qualifications) / len(
                    total_resume_set | total_job_set) if total_resume_set | total_job_set else 0

                common_skills = resume_skills.intersection(job_skills)
                skills_score = len(common_skills) / (len(resume_skills) + len(job_skills) - len(common_skills))
                # print("sim",skills_score)
                common_lang = resume_languages.intersection(job_languages)
                lang_score = len(common_lang) / (len(resume_languages) + len(job_languages) - len(common_lang))
                # print("sim",lang_score)
                common_qua = resume_education.intersection(job_education)
                qua_score = len(common_qua) / (len(resume_education) + len(job_education) - len(common_qua))
                # print("sim",qua_score)
                common_exp = resume_exp.intersection(job_exp)
                exp_score = len(common_exp) / (len(resume_exp) + len(job_exp) - len(common_exp))
                # print("sim",exp_score)
                overall_similarity = (exp_score + qua_score + lang_score + skills_score) / 4
                print("Overall Similarity Test1:", overall_similarity)
                # Calculate overall similarity score (average of individual similarities)
                overall_similarity = (skills_similarity + languages_similarity + exp_similarity + qualifications_similarity) / 4

                # print("Skills Similarity:", skills_similarity)
                # print("Languages Similarity:", languages_similarity)
                # print("exp_similarity Similarity:", exp_similarity)
                # print("Qualifications Similarity:", qualifications_similarity)
                print("Overall Similarity Test2:", overall_similarity)

                job_desc = job.job_description + job.job_qualification + job.job_responsibility + job.job_skills + " " + job.job_graduation_year + " " + job.job_CGPA + " " + job.job_languages
                # Create CountVectorizer and fit-transform the data
                vectorizer = CountVectorizer().fit_transform([job_desc, cleaned_text])

                # Compute cosine similarity
                cosine_sim = cosine_similarity(vectorizer)
                # Print the cosine similarity matrix
                print("Cosine Similarity:")
                cosine = round(cosine_sim[0, 1], ndigits=2)
                print(cosine)

                match = JobMatch.objects.create(match_score=cosine, candidate_id=request.user.id, job_id=jid,
                                                company_id=job.company_name_id)
                match.save()
                if match.job_id == jid:
                    m = 1
    else:
        m = 2
    return render(request, 'job-details.html', {'job': job, 'com': com, 'm': m})


def job_posting(request):
    jobs = ''
    try:
        jid = request.GET.get('jid')
        jobs = Jobs.objects.get(id=jid)
        jobs.d = jobs.last_date.day
        jobs.m = jobs.last_date.month
        jobs.y = jobs.last_date.year
    except:
        pass
    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        job_type = request.POST.get('job_type')
        location = request.POST.get('location')
        category = request.POST.get('category')
        job_skills = request.POST.get('job_skills')
        desc = request.POST.get('desc')
        resp = request.POST.get('resp')
        qua = request.POST.get('qua')
        year = request.POST.get('year')
        cgpa = request.POST.get('cgpa')
        exp = request.POST.get('exp')
        salary = request.POST.get('salary')
        lang = request.POST.get('lang')
        last_date = request.POST.get('last_date')
        print(request.user.id)
        employer = Employer.objects.get(admin_id=request.user.id)
        # if Jobs.objects.get(id=jid):
        try:
            jb = Jobs.objects.get(id=jid)
            jb.job_title = job_title.lower()
            jb.job_nature = job_type
            jb.job_location = location.lower()
            jb.category = category
            jb.job_skills = job_skills
            jb.job_description = desc
            jb.job_responsibility = resp
            jb.job_qualification = qua
            jb.job_graduation_year = year
            jb.job_CGPA = cgpa
            jb.job_exp = exp
            jb.job_salary = salary
            jb.job_languages = lang
            jb.last_date = last_date
            jb.save()
        except:
            job = Jobs.objects.create(company_name_id=employer.id, job_title=job_title.lower(), job_nature=job_type,
                                      job_location=location.lower(), category=category, job_description=desc,
                                      job_responsibility=resp, job_qualification=qua, job_skills=job_skills,
                                      job_graduation_year=year, job_CGPA=cgpa, job_exp=exp, job_salary=salary,
                                      job_languages=lang, last_date=last_date)
            job.save()
    return render(request, 'post-job.html', {'j': jobs})


def all_jobs(request):
    emp = Employer.objects.get(admin_id=request.user.id)
    jobs = Jobs.objects.filter(company_name_id=emp.id).order_by('-id')
    current_time = datetime.now(timezone.utc)
    print(emp.id)

    if request.method == 'POST':
        search = request.POST.get('search')
        print(search)
        if Jobs.objects.filter(company_name_id=emp.id, job_title=search.lower()).exists():
            print('search')
            jobs = Jobs.objects.filter(company_name_id=emp.id, job_title=search.lower())
        elif Jobs.objects.filter(company_name_id=emp.id, category=search).exists():
            jobs = Jobs.objects.filter(company_name_id=emp.id, category=search)
            print('search1')
        else:
            messages.warning(request, "No Jobs")
            print('search2')

    for job in jobs:
        time_diff = current_time - job.published_date
        job.time_difference = time_diff.total_seconds()
        job.minutes_ago = int(job.time_difference / 60)  # Calculate minutes ago
        job.hours_ago = int(job.time_difference / 3600)  # Calculate hours ago
        job.days_ago = int(job.time_difference / 86400)  # Calculate days ago
        job.months_ago = int(job.time_difference / (86400 * 30))
    return render(request, 'all_jobs.html', {'hot_jobs': jobs, 'logo': emp.logo.url})


# def delete_job(request):
#     jid = request.GET.get('jid')
#     j = Jobs.objects.get(id=jid)
#     j.delete()
#     return redirect(all_jobs)


def browse_jobs(request):
    jobs = Jobs.objects.all().order_by('-id')
    current_time = datetime.now(timezone.utc)
    if request.method == 'POST':
        job = request.POST.get('job')
        loc = request.POST.get('loc')
        category = request.POST.get('category')
        if Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category).exists():
            jobs = Jobs.objects.filter(job_title=job.lower(), job_location=loc.lower(), category=category)
        else:
            messages.warning(request, "No Jobs Found")

    for job in jobs:
        print(job.company_name_id)
        emp = Employer.objects.get(id=job.company_name_id)
        print(emp.logo.url)
        job.logo = emp.logo.url
        time_diff = current_time - job.published_date
        job.time_difference = time_diff.total_seconds()
        job.minutes_ago = int(job.time_difference / 60)  # Calculate minutes ago
        job.hours_ago = int(job.time_difference / 3600)  # Calculate hours ago
        job.days_ago = int(job.time_difference / 86400)  # Calculate days ago
        job.months_ago = int(job.time_difference / (86400 * 30))
    return render(request, 'browse_jobs.html', {'jobs': jobs, 'name': request.user.first_name})


def resume_upload(request):
    f = 0
    if request.method == 'POST':
        file = request.FILES['resume']
        print(file)
        print(request.user.id)
        res = Candidate.objects.get(admin_id=request.user.id)
        res.resume = file
        res.save()
        if res.resume is not None:
            f = 1
    print(f)
    return render(request, 'resume_upload.html', {'f': f, 'name': request.user.first_name })



def manage_resume(request):
    r = 0
    candidate = Candidate.objects.get(admin_id=request.user.id)
    if candidate.resume:
        pass
    else:
        r = 1
        messages.warning(request, 'Please upload Resume!')
    return render(request, 'manage_resume.html', {'resume': candidate, 'r': r})


def selected_candidate(request):
    cid = request.GET.get('cid')
    print(cid)
    emp = Employer.objects.get(admin_id=request.user.id)
    match = JobMatch.objects.filter(company_id=emp.id)
    for m in match:
        if float(m.match_score) > float(0.50):
            m.candidate = CustomUser.objects.get(id=m.candidate_id)
            try:
                if Notification.objects.filter(job=m.job_id, candidate=m.candidate_id).exists():
                    pass
                else:
                    notify = Notification.objects.create(candidate=m.candidate_id, message="Congratulations!",
                                                         employer=request.user.id, job=m.job_id)
                    notify.save()
            except:
                pass
            m.resume = Candidate.objects.get(admin_id=m.candidate_id)
            print(m.resume.resume.url)
            m.job = Jobs.objects.get(id=m.job_id)
            print(m.candidate)
        else:
            pass
    return render(request, 'selected_candidates.html', {'data': match})


def delete_candidate(request):
    id = request.GET.get('mid')
    print(id)
    match = JobMatch.objects.get(id=id)
    match.delete()
    messages.warning(request, 'Candidate Deleted Successfully!')
    return redirect(selected_candidate)


def notify(request):
    current_time = datetime.now(timezone.utc)
    notification = Notification.objects.filter(candidate=request.user.id).order_by('-id')
    if notification.exists():
        for n in notification:
            n.cand = CustomUser.objects.get(id=n.candidate)
            n.emp = Employer.objects.get(admin_id=n.employer)
            n.jobs = Jobs.objects.get(id=n.job)
            time_diff = current_time - n.time_stamp
            n.time_difference = time_diff.total_seconds()
            n.minutes_ago = int(n.time_difference / 60)  # Calculate minutes ago
            n.hours_ago = int(n.time_difference / 3600)  # Calculate hours ago
            n.days_ago = int(n.time_difference / 86400)  # Calculate days ago
            n.months_ago = int(n.time_difference / (86400 * 30))
    else:
        messages.warning(request, 'No Notifications')

    return render(request, "notification.html", {'n': notification})


def view_notification(request):
    nid = request.GET.get('nid')
    notification = Notification.objects.get(id=nid)
    notification.read_status = True
    notification.save()
    cand = CustomUser.objects.get(id=notification.candidate)
    emp = Employer.objects.get(admin_id=notification.employer)
    jobs = Jobs.objects.get(id=notification.job)

    return render(request, 'view_notification.html', {'c': cand, 'e': emp, 'j': jobs})



def delete_notification(request):
    did = request.GET.get('did')
    n = Notification.objects.get(id=did)
    n.delete()
    return redirect(notify)