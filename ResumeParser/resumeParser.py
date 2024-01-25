import re, spacy, string
from .models import Jobs

def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
    resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = re.sub('#\S+', '', resumeText)  # remove hashtags
    resumeText = re.sub('@\S+', '  ', resumeText)  # remove mentions
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~\x00"""), ' ',
                        resumeText)  # remove punctuations
    resumeText = re.sub(r'[^\x00-\x7f]', r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
    return resumeText


def extract_information_from_resume(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    punct = text.translate(str.maketrans('', '', string.punctuation + "➢•"))
    punct = punct.lower()
    #     print(punct)
    # Extract person names using named entity recognition (NER)
    person_names = [entity.text for entity in doc.ents if entity.label_ == "PERSON"]

    languages = [ent.text for ent in doc.ents if ent.label_ == "LANGUAGE"]
    for ent in ['Hindi', 'Tamil', 'Arabic', 'Telungu', 'Malayalam', 'French']:
        #         print(ent)
        if ent.lower() in punct:
            languages.append(ent)
    # Filter the identified names based on capitalization and length
    filtered_names = [name for name in person_names if len(name.split()) > 1]

    # Define a list of skills
    skills = ["Python", "Machine Learning", "Data Science", "Data Analysis", "HTML", "JavaScript", "Python Developer",
              "Java", "C", "C++", "Web Developer", "Data Analyst", "Communication Skills", "Problem-Solving", "Adaptability", "Flexibility",
              "Leadership Skills", "Accounting", "Analytical Skills", "Customer Service Skills", "Leadership", "Creativity", "Critical Thinking",
              "Time Management", "RESTful APIs", "team work", "MySQL", "PostgreSQL", "MongoDB", "CSS", "Javascript", "NoSQL", "NumPy", "Pandas", "Matplotlib",
              "Django", "Flask",  "AWS", "Azure","Google Cloud Platform", "web development", "Scrum", "Docker",  "React", "Angular", "Vue.js",
              "Express.js", "SQLite", "Jenkins", "Travis CI", "GitLab CI/CD", "NLTK", "SpaCy","CNN", "RNN", "AutoCAD", "Ethical Hacking",
              "Network Security", "Hadoop", "TensorFlow", "Google Cloud","Sketch", "Adobe XD", "Ruby", "PHP", "Swift", "Kotlin",
              "Statistical Analysis", "Regression", "Classification", "Clustering"]

    # Extract skills from the resume (basic string matching)
    skills_found = [skill for skill in skills if skill.lower() in text.lower()]

    pattern = r'(\d+)\s*(?:years?)?\s*(?:of)?\s*(?:exp(?:erience)?)'

    # Search for the pattern in the text
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Convert matched strings to integers and return the sum
    years_of_experience = []
    years_of_experience.append(sum(map(int, matches)))

    # Extract education: Degrees obtained and Graduation years
    education = []
    for ent in doc.ents:
        if ent.label_ == "DEGREE":
            print("found")
            # Extract degree and its associated tokens
            degree_tokens = [token.text for token in ent.subtree]
            # Find the graduation year if mentioned
            graduation_year = 2020
            for token in ent.subtree:
                if token.ent_type_ == "DATE":
                    graduation_year = token.text
                    break

            education.append({
                "Degree": " ".join(degree_tokens),
                "Graduation_Year": graduation_year
            })
    return {
        "Name": filtered_names[0].strip() if filtered_names else None,
        "Skills": skills_found,
        "years_of_experience": years_of_experience,
        "Languages": list(set(languages)),
        "Education": education
    }
