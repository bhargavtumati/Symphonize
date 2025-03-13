from bs4 import BeautifulSoup
import json
import os
from typing import Optional, List
from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.api.v1.endpoints.models.common_models import QuestionAnswerDict


EXTRACT_FEATURES_FROM_DESCRIPTION1 = """
You are given a Job Description given by the recruiter. 
Your task is to extract specific details from the job description and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Respond only with details in the job description . Do not give any information outside the job description
Instead of null values use empty strings.
Do not use backticks followed by json in your response.

The required keys are: 
    skills: a list of skills mentioned in the job description, each rated on a scale from 0 to 10 . 
    responsibilities: a simple list of responsibilities as an array of text given in job description.
    location : that got specified in the job description 
    softskills: a list of Softskills mentioned in the job description, each rated as Basic, Medium, or Advanced.

The required keys in each skill are:
    name: name of the skill
    type: type of skill
    rating: a rating from 0-10 based on the following scale:
      - 0: Minimal to none
      - 1: Minimal
      - 2: Minimal to below average in basics
      - 3: Average in basics
      - 4: Good in basics
      - 5: Excellent in basics with minimal understanding of advanced concepts
      - 6: Excellent in basics with basic knowledge of advanced concepts
      - 7: Excellent in basics with average knowledge of advanced concepts
      - 8: Excellent in basics with above-average knowledge of advanced concepts
      - 9: Excellent in basics with good knowledge of advanced concepts
      - 10: Excellent in both basics and advanced concepts
      
Here is the job description:
{job_description}
"""

EXTRACT_FEATURES_FROM_JOBDESCRIPTION2 = """
You are given a job description text copied by a user. 
Your task is to extract specific details from the job description and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Instead of null, Not provided, or None values, always provide plausible or imaginary values based on context or assumptions.
Do not use backticks followed by json in your response.

The required keys are: 
    skills: The list of **technical skills** (e.g., programming languages, tools, frameworks, methodologies) mentioned in the job description. These must be categorized separately from soft skills. 
    responsibilities: A list of short terms (2-3 words) summarizing responsibilities mentioned in the job description. This must always be a **list of strings** (e.g., ["Designing solutions", "Leading projects"]). 
    overall_experience: Total number of years of experience a candidate has. 
    availability: The availability provided in the job description, which should be an integer and can be one of the following: 0, 15, 30, 60, 90, and 99.
    softskills: A list of **soft skills** (e.g., communication, mentoring, collaboration) mentioned in the job description. Soft skills should not overlap with technical skills and must be categorized separately.
    transition_behaviour: The candidate's transition behaviour based on company switch, which should be an integer and can be categorized into one of the following: 0, 1, 2, 3, 4, 5.
    clarifying_questions: Identify all fields with placeholder values ("Not provided", "Any", `0`, etc.), default values, or empty lists or with missing information, and generate clarifying questions in a more precise, contextual way to reduce ambiguity. For example:
    - If "softskills" is an empty list, ask: "What soft skills are important for this role?"
    - If "availability" is `0`, ask: "What is the expected availability for this role (in days)?"
    - If no responsibilities are provided, ask: "Can you provide a list of key responsibilities for this job?"

The required keys in each skill are:
    name: name of the technical skill
    pref: the preference given in the job description, must be one of these exact values:
        1. "Good to have"
        2. "Preferred to have" 
        3. "Must have"
    value: number of years of experience [0-10]
    rating: a rating from 0-10 based on the following scale:
      - 0: Minimal to none
      - 1: Minimal
      - 2: Minimal to below average in basics
      - 3: Average in basics
      - 4: Good in basics
      - 5: Excellent in basics with minimal understanding of advanced concepts
      - 6: Excellent in basics with basic knowledge of advanced concepts
      - 7: Excellent in basics with average knowledge of advanced concepts
      - 8: Excellent in basics with above-average knowledge of advanced concepts
      - 9: Excellent in basics with good knowledge of advanced concepts
      - 10: Excellent in both basics and advanced concepts

The required keys in each soft skill are:
    name: name of the soft skill
    pref: the preference given in the job description, must be one of these exact values:
        1. "Good to have"
        2. "Preferred to have" 
        3. "Must have"
    rating: a rating based on the following scale:
      - 0: Basic
      - 1: Medium
      - 2: Advanced

**Additional instructions**: 
- Ensure soft skills and technical skills are categorized properly. For example, "mentoring," "collaboration," and "communication" should always fall under "softskills," while skills like "Java," "testing," or "design patterns" should fall under "skills."
- If a skill or term fits into both categories, use the context to decide the most appropriate category.
- Avoid duplication of skills across the "skills" and "softskills" lists.

Here is the job description:
{job_description}
"""


EXTRACT_FEATURES_FROM_JOBDESCRIPTION3 = """
You are given a job description text copied by a user. 
Your task is to extract specific details from the job description and structure them into a JSON file. Respond only with valid JSON.
Do not use backticks followed by JSON in your response.

The required keys are: 
    skills: The list of **technical skills** (e.g., programming languages, tools, frameworks, methodologies) mentioned in the job description. These must be categorized separately from soft skills. 
    responsibilities: A list of short terms (2-3 words) summarizing responsibilities mentioned in the job description. This must always be a **list of strings** (e.g., ["Designing solutions", "Leading projects"]). 
    overall_experience: Total number of years of experience a candidate has, take a maximum value if given as range.
    availability: The availability of the candidate that they are expecting join with in specified days, provided in the job description like, which should be an integer and can be one of the following: 0, 15, 30, 60, 90, and 99. 
        if the job description contains other than these take that value 
    softskills: A list of **soft skills** (e.g., communication, mentoring, collaboration) mentioned in the job description. Soft skills should not overlap with technical skills and must be categorized separately.
    transition_behaviour: The candidate's transition behaviour based on company switch, which should be an integer and can be categorized into one of the following: 0, 1, 2, 3, 4, 5.
    clarifying_questions: Identify only skills, responsibilities, overall_experience, availability, softskills and transition_behaviour fields with placeholder values ("Not provided", "Any", `0`, etc.), 
        default values, or empty lists or with missing information, and generate clarifying questions in more precise, contextual way and reduce ambiguity as a list of strings.


The required keys in each skill are:
    name: The name of the technical skill.
    pref: The preference given in the job description, must be one of these exact values:
        1. "Good to have"
        2. "Preferred to have" 
        3. "Must have"
    value: Number of years of experience [0-10].
    rating: A rating from **0-10** based on the following scale:
      - 0: Minimal to none
      - 1: Minimal
      - 2: Minimal to below average in basics
      - 3: Average in basics
      - 4: Good in basics
      - 5: Excellent in basics with minimal understanding of advanced concepts
      - 6: Excellent in basics with basic knowledge of advanced concepts
      - 7: Excellent in basics with average knowledge of advanced concepts
      - 8: Excellent in basics with above-average knowledge of advanced concepts
      - 9: Excellent in basics with good knowledge of advanced concepts
      - 10: Excellent in both basics and advanced concepts

The required keys in each soft skill are:
    name: The name of the soft skill.
    pref: The preference given in the job description, must be one of these exact values:
        1. "Good to have"
        2. "Preferred to have" 
        3. "Must have"
    rating: A rating based on the following scale:
      - 0: Basic
      - 1: Medium
      - 2: Advanced

Additional Instructions:
    Ensure soft skills and technical skills are categorized properly.
    Example: "mentoring," "collaboration," and "communication" should always fall under "softskills"
    Example: "Java," "testing," and "design patterns" should always fall under "skills"
    If a term fits both categories, use context to decide the correct placement.
    Avoid duplication of skills across "skills" and "softskills".
    Instead of null values use 'empty strings' for text fields and use '0' for numeric values

NOTE:
    - if you think that the values for the skills, softskills, responsibilities, transition_behaviour and availability are missing or insufficent then ask question to get clarity.
    - ask questions for the skills, softskills, responsibilities, transition_behaviour and availability only.
    - ask question for overall_experience if job description contains range(7-9 years of Experience), like 'what is the required overall experience for these role?'
    - ask question on transition_behaviour if the provided job description is for experienced.
    - ask questions for the fields only, not for the provided values for those fields in job description.
    - ask questions in a proper way for the person who is creating the job description. 
    - Dont ask clarifying questions on experience and rating for technical skill and soft skill that are given in job description. Give a sutiable value based on job description.
    - Dont ask clarifying questions on transition_behaviour if the provided job description is for fresher.
    - Dont ask clarifying questions more than 6.
    Example for asking the questions:
    - If "softskills" is an empty list, then ask: "What soft skills are important for this role?"

Respond only with valid JSON. Do not use backticks followed by JSON in your response.

Here is the job description:
{job_description}
"""


def validate_and_correct_enhanced_job_description(enhanced_jd):
    # Default values
    default_pref = "Preferred to have"
    default_rating = 5
    default_value = 5
    
    # Remove null values
    enhanced_jd = {k: v for k, v in enhanced_jd.items() if v is not None}
    
    # Validate skills
    if "skills" not in enhanced_jd or not isinstance(enhanced_jd["skills"], list):
        enhanced_jd["skills"] = []
    else:
        validated_skills = []
        for skill in enhanced_jd["skills"]:
            if isinstance(skill, str):  # If skill is just a string, convert it to dict
                validated_skills.append({"name": skill, "pref": default_pref, "value": default_value, "rating": default_rating})
            elif isinstance(skill, dict) and skill.get("name") is not None:
                validated_skills.append({
                    "name": skill["name"],
                    "pref": skill.get("pref", default_pref) if skill.get("pref") in ["Must have", "Good to have", "Preferred to have"] else default_pref,
                    "value": min(max(default_value if skill.get("value") is None else skill["value"], 0), 10),
                    "rating": min(max(default_rating if skill.get("rating") is None else skill["rating"], 0), 10)
                })
        enhanced_jd["skills"] = validated_skills
    
    # Validate soft skills
    if "softskills" not in enhanced_jd or not isinstance(enhanced_jd["softskills"], list):
        enhanced_jd["softskills"] = []
    else:
        validated_softskills = []
        for soft_skill in enhanced_jd["softskills"]:
            if isinstance(soft_skill, str):  # If soft skill is just a string, convert it to dict
                validated_softskills.append({"name": soft_skill, "pref": default_pref, "rating": default_rating})
            elif isinstance(soft_skill, dict) and soft_skill.get("name") is not None:
                validated_softskills.append({
                    "name": soft_skill["name"],
                    "pref": soft_skill.get("pref", default_pref) if soft_skill.get("pref") in ["Must have", "Good to have", "Preferred to have"] else default_pref,
                    "rating": min(max(default_rating if soft_skill.get("rating") is None else soft_skill["rating"], 0), 10)
                })
        enhanced_jd["softskills"] = validated_softskills
    
    # Validate responsibilities
    if "responsibilities" not in enhanced_jd or not isinstance(enhanced_jd["responsibilities"], list):
        enhanced_jd["responsibilities"] = []
    # else:
    #     enhanced_jd["responsibilities"] = enhanced_jd["responsibilities"][:20]  # Limit to 20 items
    
    # Validate integer fields
    if "availability" not in enhanced_jd or not isinstance(enhanced_jd["availability"], int) or enhanced_jd["availability"] < 0:
        enhanced_jd["availability"] = 0
    elif enhanced_jd["availability"] > 99:
        enhanced_jd["availability"] = 99
    
    if "transition_behaviour" not in enhanced_jd or not isinstance(enhanced_jd["transition_behaviour"], int) or enhanced_jd["transition_behaviour"] < 0:
        enhanced_jd["transition_behaviour"] = 0
    elif enhanced_jd["transition_behaviour"] > 50:
        enhanced_jd["transition_behaviour"] = 50
    
    if "overall_experience" not in enhanced_jd or not isinstance(enhanced_jd["overall_experience"], int) or enhanced_jd["overall_experience"] < 0:
        enhanced_jd["overall_experience"] = 0
    
    return enhanced_jd


def extract_features_from_jd(
    text:str,
    prompt_template: str = EXTRACT_FEATURES_FROM_JOBDESCRIPTION3,
    ai_clarifying_questions: Optional[List[QuestionAnswerDict]] = None,
    enable_parser: bool = False,
    output_format: str = "json",
    max_retries: int = 4,
    api_key: Optional[str] = None,  # Optional parameter for flexibility
) -> str:


    if not text:
        return json.dumps({"error": "No text could be extracted from the file or provided text is empty."})
    
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text(separator="\n", strip=True)

    clarifying_answers = {}
    if ai_clarifying_questions:
        clarifying_answers = {q.question: q.answer for q in ai_clarifying_questions}

    if not clarifying_answers:
        clarifying_answers_context = "No additional clarifications were provided."
    else:
        clarifying_answers_context = "\n".join(
            [f"{question}: {answer}" for question, answer in clarifying_answers.items()]
        )

    # Initialize LLM with the provided API key
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GEMINI_API_KEY"),  # Replace with your actual key
        model=os.getenv("CHAT_GENAI"),
        temperature=0.7,
        top_p=0.85
    )
    
    print(f"the text data is : {text}")

    combined_text = f"Job Description:\n{text}\n\nClarifying Answers:\n{clarifying_answers_context}"

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables={"text"},  # Consistent dictionary syntax
    )

    input_data = {"job_description": combined_text}
    chain = prompt | llm

    # Retry loop for handling transient JSON parsing issues
    for attempt in range(max_retries):
        response = chain.invoke(input_data)
        response_content = response.content
        print(f"the response is : {response_content}")
        try:
            data = json.loads(response_content)
            data = validate_and_correct_enhanced_job_description(data)
            return data
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    # Final attempt outside of retries, or error handling if all attempts fail
    try:
        response_json = json.loads(response_content)
        response_json = validate_and_correct_enhanced_job_description(response_json)
        # response_json["text"] = text
        return response_json
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse JSON response after retries."})
