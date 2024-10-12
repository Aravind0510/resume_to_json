from flask import Flask, request, jsonify, render_template, send_file
import os
import json
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def parse_resume(resume_text):
    parsed_data = {
        "Personal Information": {},
        "Education": {},
        "Skills": [],
        "Experience": [],
        "Projects": [],
        "Certifications": []
    }

    # Extract Personal Information
    personal_info_pattern = r"Name:\s*(.*)\nEmail:\s*(.*)\nPhone:\s*(.*)\nLinkedIn:\s*(.*)"
    personal_info_match = re.search(personal_info_pattern, resume_text)
    if personal_info_match:
        parsed_data["Personal Information"] = {
            "Name": personal_info_match.group(1),
            "Email": personal_info_match.group(2),
            "Phone": personal_info_match.group(3),
            "LinkedIn": personal_info_match.group(4),
        }

    # Extract Education
    education_pattern = r"Education:\s*(.*)\nDegree:\s*(.*)\nMajor:\s*(.*)\nUniversity:\s*(.*)\nGraduation Year:\s*(.*)\nCGPA:\s*(.*)"
    education_match = re.search(education_pattern, resume_text)
    if education_match:
        parsed_data["Education"] = {
            "Degree": education_match.group(2),
            "Major": education_match.group(3),
            "University": education_match.group(4),
            "Graduation Year": education_match.group(5),
            "CGPA": education_match.group(6)
        }

    # Extract Skills
    skills_pattern = r"Skills:\s*(.*)"
    skills_match = re.search(skills_pattern, resume_text)
    if skills_match:
        parsed_data["Skills"] = [skill.strip() for skill in skills_match.group(1).split(",")]

    # Extract Experience
    experience_pattern = r"Experience:\s*(.*)"
    experience_match = re.search(experience_pattern, resume_text, re.DOTALL)
    if experience_match:
        experiences = experience_match.group(1).strip().split("\n\n")
        for exp in experiences:
            exp_lines = re.split(r"\n", exp)
            if len(exp_lines) >= 4:
                job_title, company, location, dates = exp_lines[:4]
                responsibilities = exp_lines[4] if len(exp_lines) > 4 else ""
                parsed_data["Experience"].append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": location,
                    "Dates Employed": dates,
                    "Responsibilities": responsibilities.split(", ")
                })

    # Extract Projects
    projects_pattern = r"Projects:\s*(.*)"
    projects_match = re.search(projects_pattern, resume_text, re.DOTALL)
    if projects_match:
        projects = projects_match.group(1).strip().split("\n\n")
        for proj in projects:
            proj_lines = re.split(r"\n", proj)
            if len(proj_lines) >= 3:
                title, description, tech_stack = proj_lines[:3]
                github = proj_lines[3] if len(proj_lines) > 3 else ""
                parsed_data["Projects"].append({
                    "Title": title,
                    "Description": description,
                    "Tech Stack": tech_stack.split(", "),
                    "GitHub Link": github
                })

    # Extract Certifications
    certifications_pattern = r"Certifications:\s*(.*)"
    certifications_match = re.search(certifications_pattern, resume_text, re.DOTALL)
    if certifications_match:
        certs = certifications_match.group(1).strip().split("\n\n")
        for cert in certs:
            cert_lines = re.split(r"\n", cert)
            if len(cert_lines) >= 3:
                title, organization, date = cert_lines[:3]
                parsed_data["Certifications"].append({
                    "Title": title,
                    "Issuing Organization": organization,
                    "Date": date
                })

    return parsed_data

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        with open(filepath, 'r') as f:
            resume_content = f.read()

        parsed_json = parse_resume(resume_content)

        # Save the parsed JSON
        output_path = os.path.join('uploads', 'output.json')
        with open(output_path, 'w') as json_file:
            json.dump(parsed_json, json_file, indent=4)
        
        return send_file(output_path, as_attachment=True, download_name='resume_parsed.json')

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
