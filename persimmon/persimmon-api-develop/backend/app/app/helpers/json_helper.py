from app.helpers.data_helper import reformat_date


# Flattening function
async def flatten_resume_data(data):
    all_responsibilities=[]
    if data.get("experience"):
        for experience in data["experience"]:
            responsibilities = experience.get("responsibilities", [])
            all_responsibilities.extend(responsibilities)
    flattened_data = {
        "about": data["personal"].get("about", ""),  
        "personal_information": {
            "full_name": data["personal"].get("name", ""),
            "date_of_birth": data["personal"].get("date_of_birth", ""),
            "gender": data["personal"].get("gender", ""),
            "address": data["personal"].get("address",""),  # Assuming address is missing from original JSON
            "phone": data["personal"].get("phone", ""),
            "email": data["personal"].get("email", "")
        },
        "job_information": {
            "job_title": data["experience"][0].get("title", "") if data["experience"] else "",
            "department": "",  # Department is missing from original JSON
            "current_work_at": data["experience"][0].get("company", "") if data["experience"] else "",
            "job_location": data["experience"][0].get("location", "") if data["experience"] else "",
            "work_experience": data.get("overall_experience", 0),
            "current_ctc": data.get("salary", 0),
            "expected_ctc": data.get("salary", 0),
            "skills": [skill["name"] for skill in data["skills"]] if data["skills"] else []
        },
        "social_media": {
            "linkedin": next((link for link in data["personal"].get("social", []) if "linkedin" in link), ""),
            "github": next((link for link in data["personal"].get("social", []) if "github" in link), ""),
            "instagram": next((link for link in data["personal"].get("social", []) if "instagram" in link), ""),
            "facebook": next((link for link in data["personal"].get("social", []) if "facebook" in link), "")
        }
    }
    
    return flattened_data


async def flatten_resume_data_solr(data):
    all_responsibilities=[]
    if data.get("experience"):
        for experience in data["experience"]:
            responsibilities = experience.get("responsibilities", [])
            all_responsibilities.extend(responsibilities)
    flattened_data = {
        "about": data.get("personal", {}).get("about") or "",  
        "full_name": data.get("personal", {}).get("name") or "",
        "date_of_birth": reformat_date(data["personal"].get("date_of_birth", "")),
        "gender": data["personal"].get("gender", ""),
        "address": data["personal"].get("address",""),  # Assuming address is missing from original JSON
        "phone": data["personal"].get("phone", ""),
        "email": data["personal"].get("email", ""),
        "job_title": data["experience"][0].get("title", "") if data["experience"] else "",
        "department": "",  # Department is missing from original JSON
        "current_work_at": data["experience"][0].get("company", "") if data["experience"] else "",
        "job_location": data["experience"][0].get("location", "") if data["experience"] else "",
        "work_experience": data.get("overall_experience", 0),
        "current_ctc": data.get("salary", 0),#salary
        "expected_ctc": data.get("salary", 0),
        "skills": [skill["name"] for skill in data["skills"]] if data["skills"] else [],
        "linkedin": next((link for link in data["personal"].get("social", []) if "linkedin" in link), ""),
        "github": next((link for link in data["personal"].get("social", []) if "github" in link), ""),
        "instagram": next((link for link in data["personal"].get("social", []) if "instagram" in link), ""),
        "facebook": next((link for link in data["personal"].get("social", []) if "facebook" in link), ""),
        "industry_type": data.get("Industry_type", ""),
        "responsibilities": all_responsibilities,
        "company": [experience.get("company") for experience in data.get("experience", [])],
        "education" : [education.get("institution")for education in data.get("education",[])],
        "availability" : data.get("availability",""),
        "workmode" : data.get("workmode",""),
        "locations_list": [experience.get("location") for experience in data.get("experience", [])],
        "transition_behaviour": data.get("Transition_behaviour",""),
        "company_size": data.get("Company_size",""),
        "soft_skills": [soft_skill["name"] for soft_skill in data["softskills"]] if data["softskills"] else [],
        "team_size": data.get("Team_size"," ")  
    }
    return flattened_data