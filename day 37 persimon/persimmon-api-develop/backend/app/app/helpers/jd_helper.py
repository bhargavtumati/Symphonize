from bs4 import BeautifulSoup
import json
import os
from typing import Optional
from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


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
You are given a resume text copied by a user. 
Your task is to extract specific details from the resume and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Instead of null, Not provided, or None values, always provide plausible or imaginary values based on context or assumptions.
Do not use backticks followed by json in your response.

The required keys are: 
    Industry_type: The industry type of the Company that is given in job description for job applicants (Based on the company comeup with some values Ex: "IT Services and IT Consulting", "Banking", "Investment Management") . 
    salary: the salary mentioned in job description as LPA (caluculate accoding to his experience) . 
    skills: the list of skills in the job description . 
    responsibilities : list of responsibilities in the job description , try to come up with the short 2 to 3 word terms for responsibilities. 
    overall_experience: total number of years of experience a candidate has.
    availability: The availability provided in job description (the value should be in between 0 to 90).
    workmode: the preferred work mode, which can be one of the following: "Any", "Work from Home" , "Work from Office", "Hybrid".
    location : The location that was mentioned in the job description . 
    softskills: a list of Softskills mentioned in the job description .
    Transition_behaviour: the candidate's transition behaviour based of company switch (The value should foolow these example : 0-5 (or) >5 ). 
    Company_size : The size of the company the job description is expecting  (give some estimates of you with numbers example like 1-100 ) . 
    Team_size : the size of the team the job description is expecting (give some estimates of you). 

The required keys in industry type are:
    name: Type of the industry given in description (if it is not there come up with something using job description)
    preference : the preference that given in job description (if the thing is not given come up with some value amoung these 1. Good to have ,2. Prefer to have , 3.Must have)
    min_experience: the minimum experience in working in that industry (give the scale in terms of 0-9)
    max_experience: the maximum experience in working in that industry (give the scale in terms of 0-9) 

The required keys in the Salary type are:
    min_value : minimum value of Salary 
    max_value : maximum value of Salary 

The required keys in each skill are:
    name: name of the skill
    preference: the preference that given in job description (if the thing is not given come up with some value amoung these 1. Good to have ,2. Prefer to have , 3.Must have)
    experience: number of years of experience
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
    preference: the preference that given in job description (if the thing is not given come up with some value amoung these 1. Good to have ,2. Prefer to have , 3.Must have)
    rating: a rating should be based on the following scale:
      - 0: Basic
      - 1: Medium
      - 2: Advanced

The required keys in Company size are :
    preference: the preference that given in job description (if the thing is not given come up with some value amoung these 1. Good to have ,2. Prefer to have , 3.Must have)
    value : the value specified in the job description (if not come up with some values like 1-100 , 100-200 )

Here is the resume:
{job_description}
"""



def extract_features_from_jd(
    text:str,
    prompt_template: str = EXTRACT_FEATURES_FROM_JOBDESCRIPTION2,
    enable_parser: bool = False,
    output_format: str = "json",
    max_retries: int = 2,
    api_key: Optional[str] = None,  # Optional parameter for flexibility
) -> str:


    if not text:
        return json.dumps({"error": "No text could be extracted from the file or provided text is empty."})
    
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text(separator="\n", strip=True)

    # Initialize LLM with the provided API key
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GEMINI_API_KEY"),  # Replace with your actual key
        model="gemini-pro",
        temperature=0.7,
        top_p=0.85
    )
    
    print(f"the text data is : {text}")

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables={"text"},  # Consistent dictionary syntax
    )

    input_data = {"job_description": text}
    chain = prompt | llm

    # Retry loop for handling transient JSON parsing issues
    for attempt in range(max_retries):
        response = chain.invoke(input_data)
        response_content = response.content
        print(f"the response is : {response_content}")
        try:
            data = json.loads(response_content)
            print(f"the data is :{data}")
            return data
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    # Final attempt outside of retries, or error handling if all attempts fail
    try:
        response_json = json.loads(response_content)
        # response_json["text"] = text
        return json.dumps(response_json, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse JSON response after retries."})
