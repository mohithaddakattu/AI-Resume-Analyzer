def extract_skills(text):

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "Flask",
        "React",
        "MongoDB",
        "Machine Learning",
        "Data Structures",
        "Spring Boot"
    ]

    found_skills = []

    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills