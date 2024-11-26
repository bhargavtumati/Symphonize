import google.generativeai as genai
import os
from fastapi import FastAPI

app = FastAPI()

# Set your API key as an environment variable
os.environ["API_KEY"] = "AIzaSyBRlUbGFM6zxSi2Yo8Ge8SbDiPTkwJLzTk"

# Configure the API key
genai.configure(api_key=os.environ["API_KEY"])

# Create a model instance
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate content
@app.get("/generatejd")
async def generate_jd(job_title: str, experience :str, package:str, location:str, job_type:str, company:str, skills:str):
        response = model.generate_content(f"generate jd for {job_title} where experience need to be {experience} years having package {package} lakhs and hiring location is {location} and nature of job is {job_type} company name is {company} having skills {skills}")
        return response.text

@app.get("/prompthere")
async def generate_prompt(prompt: str):
        response = model.generate_content(prompt)
        return response.text





