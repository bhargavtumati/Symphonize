from datetime import datetime
import json
import os
import re
from typing import Optional

from app.helpers.work_exp_helper import process_resume_json
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


def preprocess_resume_dates(text):
    """Preprocess resume text to standardize date formats and handle present/current dates."""
    import re
    
    # Present terms that should be replaced with current date
    present_terms = [
        "present", "Present", "current", "Current",
        "till date", "Till date", "Till Date", "till Date",
        "ongoing", "Ongoing"
    ]
    
    # Month mappings
    month_map = {
        "Jan": "01", "January": "01",
        "Feb": "02", "February": "02",
        "Mar": "03", "March": "03",
        "Apr": "04", "April": "04",
        "May": "05",
        "Jun": "06", "June": "06",
        "Jul": "07", "July": "07",
        "Aug": "08", "August": "08",
        "Sep": "09", "September": "09",
        "Oct": "10", "October": "10",
        "Nov": "11", "November": "11",
        "Dec": "12", "December": "12"
    }
    
    # First standardize the present/current terms
    current_date = datetime.now().strftime("%m/%Y")
    for term in present_terms:
        if term in text:
            text = text.replace(term, current_date)
    
    # Function to convert date to standard format
    def standardize_date(date_str):
        date_str = date_str.strip()
        
        # Handle text month format (Dec 2022, December 2022)
        for month in month_map:
            if month in date_str:
                year = re.search(r'\d{4}', date_str).group()
                return f"{month_map[month]}/{year}"
        
        # Handle MM-YYYY or MM/YYYY
        match = re.search(r'(\d{1,2})[-/](\d{4})', date_str)
        if match:
            month, year = match.groups()
            return f"{int(month):02d}/{year}"
        
        # Handle YYYY-MM or YYYY/MM
        match = re.search(r'(\d{4})[-/](\d{1,2})', date_str)
        if match:
            year, month = match.groups()
            return f"{int(month):02d}/{year}"
            
        return date_str
    
    # Find date ranges and process them
    def process_date_range(match):
        full_range = match.group()
        dates = [d.strip() for d in full_range.split('-')]
        if len(dates) != 2:
            return full_range
            
        start_date = standardize_date(dates[0])
        end_date = standardize_date(dates[1])
        
        return f"{start_date} - {end_date}"
    
    # Process all date ranges in the text
    date_pattern = r'\b(?:\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}|(?:' + '|'.join(month_map.keys()) + r')\s+\d{4})\s*-\s*(?:\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}|01/2025)\b'
    text = re.sub(date_pattern, process_date_range, text)
    
    return text


class APIKeyRotator:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_index = 0

    def get_next_key(self):
        key = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        return key
    
key1 = os.getenv("KEY_1")
key2 = os.getenv("KEY_2")
key3 = os.getenv("KEY_3")
key4 = os.getenv("KEY_4")

api_key_rotator = APIKeyRotator([key1, key2, key3, key4])

# Function to get the next key
def get_key():
    return api_key_rotator.get_next_key()


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
**strictly avoid giving output in markdown format, only give in valid json format not in invalid json format which causes json decode error. The object should not start with ```json and end with ```**
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


EXTRACT_FEATURES_FROM_RESUME_DATE2 = """You are given a resume text copied by a user. 
Your task is to extract specific details from the resume and structure them into a JSON file. 
**strictly avoid giving output in markdown format, only give in valid json format not in invalid json format which causes json decode error. The object should not start with ```json and end with ```**
Respond only with valid JSON. Do not write an introduction or summary.

# MANDATORY PRE-PROCESSING STEP: Date Standardization
Before processing ANY part of the resume, you MUST first standardize ALL dates using these rules:

1. Date Conversion Rules:
   Convert ALL dates to format "MM/YYYY" where:
   - MM is a 2-digit month (01-12)
   - YYYY is a 4-digit year
   - The separator MUST be "/"

   Input Format → Required Output:
   - "2023-01" → "01/2023"
   - "Jan 2023" → "01/2023"
   - "January 2023" → "01/2023"
   - "2023" → "01/2023"
   - "2023-01 - present" → "01/2023 - 01/2025"
   - "Jan 2023 - current" → "01/2023 - 01/2025"
   - "2023-01 - 2024-12" → "01/2023 - 12/2024"

2. Month Standardization Table:
   - January/Jan → "01"
   - February/Feb → "02"
   - March/Mar → "03"
   - April/Apr → "04"
   - May → "05"
   - June/Jun → "06"
   - July/Jul → "07"
   - August/Aug → "08"
   - September/Sep → "09"
   - October/Oct → "10"
   - November/Nov → "11"
   - December/Dec → "12"

3. Current Date References:
   Replace ANY of these terms with "{current_date}":
   - "present"
   - "current"
   - "till date"
   - "ongoing"
   - "till now"
   - "to date"

4. Date Range Format:
   - Must be in format: "MM/YYYY - MM/YYYY"
   - Example: "12/2022 - 01/2025"

5. PROHIBITED Formats - NEVER use:
   ❌ YYYY-MM format
   ❌ Text month names
   ❌ Single-digit months
   ❌ The word "present" or "current"
   ❌ Dates without months
   ❌ Wrong separators (like "-" instead of "/")

# Required JSON Structure

The output must be a JSON object with these exact keys (structure shown with double curly braces to escape template variables):

```json
{{
  "personal": {{
    "name": "string",
    "phone": "string",
    "email": "string",
    "address": "string",
    "gender": "string",
    "date_of_birth": "string",
    "social": ["string"],
    "about": "string"
  }},
  "skills": [
    {{
      "name": "string",
      "type": "string",
      "experience": "number",
      "rating": "number 0-10"
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "dates": "MM/YYYY - MM/YYYY"
    }}
  ],
  "experience": [
    {{
      "title": "string",
      "company": "string",
      "dates": "MM/YYYY - MM/YYYY",
      "location": "string",
      "responsibilities": ["string"],
      "experience_years": "number"
    }}
  ],
  "overall_experience": "number",
  "salary": "number",
  "Industry_type": "string",
  "availability": "number",
  "workmode": "string",
  "softskills": ["string"],
  "Transition_behaviour": "number",
  "Company_size": "string",
  "Team_size": "number"
}}
```

Ratings scale for skills:
0: Minimal to none
1: Minimal
2: Minimal to below average in basics
3: Average in basics
4: Good in basics
5: Excellent in basics with minimal understanding of advanced concepts
6: Excellent in basics with basic knowledge of advanced concepts
7: Excellent in basics with average knowledge of advanced concepts
8: Excellent in basics with above-average knowledge of advanced concepts
9: Excellent in basics with good knowledge of advanced concepts
10: Excellent in both basics and advanced concepts

# Experience Calculation Examples:
For date range "01/2023 - 01/2025":
- Start: January 2023
- End: January 2025
- experience_years = 2.0

For date range "03/2022 - 01/2025":
- Start: March 2022
- End: January 2025
- experience_years = 2.8

Rules for missing information:
1. Use empty string "" instead of null
2. For missing dates, infer based on context
3. For missing ratings, use reasonable estimates based on experience
4. For missing locations, use empty string
5. For missing team/company size, infer from context

Note:
    - do not consider the projects under the experience, consider only interships and work experience under experience key

Here is the resume:
{resume}
"""

# if the text does not contain any range for internship and given as 3 or 6 or 9 months of internship then consider that 3 or 6 or 9 months only and assign as some range of dates to match that internship.


async def extract_features_from_resume(
    text: str,
    type: str = "resume",
    prompt_template: str = EXTRACT_FEATURES_FROM_RESUME_DATE2,
    enable_parser: bool = False,
    output_format: str = "json",
    max_retries: int = 4,
    api_key: Optional[str] = None,  # Optional parameter for flexibility
) -> str:
    text = remove_special_characters(text)
    text = preprocess_resume_dates(text)
    # Initialize LLM with the provided API key
    api_key = api_key or api_key_rotator.get_next_key()
    #print("Using API key:", api_key)
    
    llm = ChatGoogleGenerativeAI(
        google_api_key = api_key,  # Replace with your actual key
        model=os.getenv("CHAT_GENAI"),
        temperature=0.7,
        top_p=0.85
    )
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables={"text", "current_date"},  # Consistent dictionary syntax
    ) 
   
    input_data = {"resume": text, "current_date": datetime.now().strftime("%m/%Y")}
    chain = prompt | llm

    # Retry loop for handling transient JSON parsing issues
    for attempt in range(max_retries):
        try:
            response = chain.invoke(input_data)
            print('lang chain response',response)
        except Exception as e:
            return e

        response_content = response.content
        print('response_content', response_content)
        pattern = r"\{.*\}"
        match = re.search(pattern, response_content, re.DOTALL)
        if match:
            result = match.group()
        response_content = result if result else response_content
        # try:
        #     response_content = response.content
        # except Exception as e :
        #     print("this is the respnse content error ",e)
        try:
            # cleaned_data = remove_special_characters(response_content)
            # print("the  cleaned data :",cleaned_data)
            response_json = json.loads(response_content)
            exp_result = process_resume_json(response_json)
            response_json['overall_experience'] = exp_result['total_experience']
            print('response_json',response_json)
            # response_json["text"] = text  # Adding original text if needed
            return json.dumps(response_json, indent=2)
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    # Final attempt outside of retries, or error handling if all attempts fail
    try:
        response_json = json.loads(response_content)
        exp_result = process_resume_json(response_json)
        response_json['overall_experience'] = exp_result['total_experience']
        response_json["text"] = text
        print('response_json',response_json)
        return json.dumps(response_json, indent=2)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")