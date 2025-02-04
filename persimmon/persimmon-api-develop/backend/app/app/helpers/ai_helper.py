import json
import os
import re
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from the .env file
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_ai_response(input: str):
    model = genai.GenerativeModel(os.getenv("GENAI"))
    response = model.generate_content(input)
    return response.text



def remove_special_characters(data):
    print("entered the re block",type(data))
    data_result = re.sub(r'[^\x00-\x7F]+', '', data)
    print("the function after tehe processing ",data_result)
    return data_result



EXTRACT_FEATURES_FROM_RESUME1 = """
You are given a resume text copied by a user. 
Your task is to extract specific details from the resume and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Instead of null values use empty strings.
Do not use backticks followed by json in your response.

The required keys are: 
    personal: personal information like name, phone, email, address , gender ,date of birth and social presence(linkedin,facebook,github,instagram).
    skills: a list of skills mentioned in the resume. 
    education: the education details (degrees, institutions, and dates). 
    experience: a list of work experience, where each entry includes the job title, company name, dates worked, location, and responsibilities. 
    overall_experience: total number of years of experience a candidate has.
    salary: the candidate's expected salary (caluculate accoding to his experience).
    availability: the candidate's availability, which can be one of the following: <15, >30, <45.
    workmode: the preferred work mode, which can be one of the following: WFH, WFO, HYB.
    softskills: the candidate's soft skills, which can be Basic, Intermediate, or Advanced.

The required keys in personal are:
    name: name of the person
    phone: phone number of the person
    email: email of the person
    address: full address of the person (including street, city, state, and zip code)
    gender: gender of the person
    date_of_birth: date of birth of the person
    social: list of links to social as an array of text
    about: the text that describes the about section of resume 

The required keys in each skill are:
    name: name of the skill
    type: type of skill
    experience: number of years of experience

The required keys in experience are:
    title: job title
    company: name of the company
    dates: dates worked
    location: place of work
    responsibilities: a simple list of responsibilities as an array of text

Here is the resume:
{resume}
"""

EXTRACT_FEATURES_FROM_RESUME2 = """You are given a resume text copied by a user. 
Your task is to extract specific details from the resume and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Instead of null values, use empty strings. Do not give "None" in the response. If something is missing, infer a reasonable value based on the context provided in the resume.

The required keys are: 
    personal: 
      name: name of the person
      phone: phone number of the person
      email: email of the person
      address: full address of the person (including street, city, state, and zip code)
      gender: gender of the person (if missing, assign an empty string)
      date_of_birth: date of birth of the person
      social: list of links to social as an array of text
      about: the text that describes the about section of resume (if missing, assign an empty string)

    skills: 
        - name: name of the technical skill
        - type: type of skill
        - experience: number of years of experience. **Never be null**; always assign a reasonable estimate based on the candidate’s experience and resume context.
        - rating: a rating from 0-10 based on the following scale:
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
             - 10: Excellent in both basics and advanced concepts. **Never return null for rating; always assign a reasonable estimate** based on the resume.

    education: 
      - degree: degree earned
      - institution: name of the institution
      - dates: dates of attendance

    experience: 
     - title: job title
     - company: name of the company
     - dates: dates worked
     - location: place of work
     - responsibilities: a simple list of responsibilities as an array of text
     - experience_years: **Calculate the number of years of experience for this specific role.** If "present" is mentioned in the `dates` field, calculate experience up to the current date. Round to one decimal place.

   overall_experience: Total number of years of experience a candidate has, **accurately calculated** based on the `experience_years` from the `experience` section. Round to one decimal place.

   salary: The candidate's expected salary. If it's not provided in the resume, **infer a reasonable estimate based on their experience and role** and return it as a float (e.g., 75000.0).
   Industry_type: The industry type of the company the candidate is currently working at (e.g., "IT Services and IT Consulting", "Banking", "Investment Management", etc.). **If not directly available**, infer the industry type based on the company name and context.
   availability: The candidate's availability, which should be an integer from the following options: 0, 15, 30, 60, 80, 90. If not mentioned, **assign a reasonable default value** based on the work experience.
   workmode: The preferred work mode, which can be one of the following: "Any", "Work from Home", "Work from Office", "Hybrid". **If not mentioned, assign a reasonable default**.
   softskills: A list of **soft skills** (e.g., communication, mentoring, collaboration) mentioned in the job description. Soft skills should not overlap with technical skills and must be categorized separately.
   Transition_behaviour: The candidate's transition behaviour based on company switches. Use one of the following values: 0 (No job switches), 1 (One job switch), 2 (Two job switches), etc., up to 5. **Use the experience section to infer this value** based on the number of different companies listed.
   Company_size: The size of the company the candidate is currently working in, based on the company context. If not mentioned directly, **infer a reasonable estimate** based on the company’s industry and known size.
   Team_size: The size of the team the candidate is currently working in. If not mentioned directly, **infer a reasonable estimate** based on the role and responsibilities. 

   
**Important Notes for Experience Calculations:**  
1. If "present" or "current" or "till date" is mentioned in the `dates` field, calculate experience up to the current date (e.g., January 2025). Use the actual current date to ensure accuracy.  
2. Use the `datetime` library for accurate date parsing.  
3. Always calculate the duration in years and months, then convert to decimal form and round to two decimal place.  
4. Examples:  
   - **"05-2022 to present"**: Calculate from May 2022 to January 2025 = 2 years and 8 months = **2.80**.  
   - **"07-2024 to 10-2024"**: Calculate from July 2024 to October 2024 = 3 months = **0.30**.  
   - **"01/2019 - 12/2021"**: Calculate from January 2019 to December 2021 = 3 years = **3.0**.  
   - **"2020 - present"**: Assume the start month is January 2020, and calculate up to January 2025 = 5 years = **5.0**.  
   - **"2021"**: If only the year is mentioned, assume January as the start month and December as the end month.
   - **"Sep 2020 - present"**: Calculate from September 2020 to January 2025 = 4 years and 4 months = **4.4**.
   - **"May 2018 - current"**: Calculate from May 2018 to January 2025 = 6 years and 8 months = **6.8**. 
   - **"june 2018 - till date"**: Calculate from May 2018 to January 2025 = 6 years and 7 months = **6.7**. 
   - **"2017 - 2021"**: Assume January 2017 to December 2021 = 5 years = **5.0**.
   - **"March 2022 to present"** : Calculate from March 2022 to January 2025 = 2 years and 10 months = **2.10**.    

**Edge Cases:**  
- If the dates are ambiguous (e.g., only the year is provided), make a reasonable assumption for start and end months as noted above.  
- If the date format cannot be parsed (e.g., non-standard formats), use `"Unknown"` for the start/end date and exclude it from experience calculations.

Here is the resume:
{resume}
"""


async def extract_features_from_resume(
    text: str,
    type: str = "resume",
    prompt_template: str = EXTRACT_FEATURES_FROM_RESUME2,
    enable_parser: bool = False,
    output_format: str = "json",
    max_retries: int = 4,
    api_key: Optional[str] = None,  # Optional parameter for flexibility
) -> str:
    text = remove_special_characters(text)
    # Initialize LLM with the provided API key
    llm = ChatGoogleGenerativeAI(
        google_api_key = os.getenv("GEMINI_API_KEY"),  # Replace with your actual key
        model=os.getenv("CHAT_GENAI"),
        temperature=0.7,
        top_p=0.85
    )
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables={"text"},  # Consistent dictionary syntax
    ) 
   
    input_data = {"resume": text}
    chain = prompt | llm

    # Retry loop for handling transient JSON parsing issues
    for attempt in range(max_retries):
        try:
            response = chain.invoke(input_data)
        except Exception as e:
            return e
        response_content = response.content
        # try:
        #     response_content = response.content
        # except Exception as e :
        #     print("this is the respnse content error ",e)
        try:
            # cleaned_data = remove_special_characters(response_content)
            # print("the  cleaned data :",cleaned_data)
            response_json = json.loads(response_content)
            # response_json["text"] = text  # Adding original text if needed
            return json.dumps(response_json, indent=2)
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    # Final attempt outside of retries, or error handling if all attempts fail
    try:
        response_json = json.loads(response_content)
        response_json["text"] = text
        return json.dumps(response_json, indent=2)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")