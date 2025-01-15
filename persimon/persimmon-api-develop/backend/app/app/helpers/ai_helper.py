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

EXTRACT_FEATURES_FROM_RESUME2 = """
You are given a resume text copied by a user. 
Your task is to extract specific details from the resume and structure them into a JSON file. 
Respond only with valid JSON. Do not write an introduction or summary.
Instead of null values use empty strings.
Do not use backticks followed by json in your response.
Do not give "None" in the response, if you find something is missing there are examples provided by me ,so come up with one  

The required keys are: 
    personal: personal information like name, phone, email, address , gender ,date of birth and social presence(linkedin,facebook,github,instagram).
    skills: a list of skills mentioned in the resume, each rated on a scale from 0 to 10 . 
    education: the education details (degrees, institutions, and dates). 
    experience: a list of work experience, where each entry includes the job title, company name, dates worked, location, and responsibilities. 
    overall_experience: total number of years of experience a candidate has.
    salary: the candidate's expected salary (caluculate accoding to his experience if it is not provided in resume text and only give float datatype).
    Industry_type: The industry type of the Company he is currently working in (Based on the company comeup with some values Ex: "IT Services and IT Consulting", "Banking", "Investment Management") . 
    availability: The candidate's availability, which should be an integer can be one of the following: 0, 15, 30, 60, 80,90 .
    workmode: the preferred work mode, which can be one of the following: "Any", "Work from Home" , "Work from Office", "Hybrid".
    softskills: a list of Softskills mentioned in the resume, each rated as Basic, Medium, or Advanced.
    Transition_behaviour: the candidate's transition behaviour based of company switch . which should be an integer can be categorized to one of the following : 0, 1, 2, 3, 4, 5  . 
    Company_size : The size of the company he is currently working in (give some estimates of you from this list ["1-10", "11-50", "51-200", "201-500","501-1000", "1001-5000", "5001-10000", "10001+"]) . 
    Team_size : the size of the team he is currently working in (give some estimates of you from this list ["1-5", "6-10", "11-20", "21-50", "51-100", "101-200", "201+"] ). 

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
The required keys in experience are:
    title: job title
    company: name of the company
    dates: dates worked
    location: place of work
    responsibilities: a simple list of responsibilities as an array of text

Here is the resume:
{resume}
"""


async def extract_features_from_resume(
    text: str,
    type: str = "resume",
    prompt_template: str = EXTRACT_FEATURES_FROM_RESUME2,
    enable_parser: bool = False,
    output_format: str = "json",
    max_retries: int = 3,
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
        response = chain.invoke(input_data)
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