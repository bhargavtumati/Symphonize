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
    pref: the preference given in the job description (if the thing is not given, come up with some value among these: 1. Good to have, 2. Preferred to have, 3. Must have)
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
    pref: the preference given in the job description (if the thing is not given, come up with some value among these: 1. Good to have, 2. Preferred to have, 3. Must have)
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
        google_api_key= os.getenv("GEMINI_API_KEY"),  # Replace with your actual key
        model="gemini-pro",
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
    


# description: str = "<p><strong>Java Developer with 2+ Years of Experience</strong></p>\n<p><strong>Overview:</strong></p>\n<p>We seek an exceptional Java Developer with proven expertise to join our dynamic and innovative team. The ideal candidate will have a deep understanding of Java programming and a track record of delivering scalable, high-quality applications.</p>\n<p><strong>Key Responsibilities:</strong></p>\n<ul>\n<li>Design, develop, and maintain enterprise-grade Java applications adhering to industry best practices and design patterns.</li>\n<li>Collaborate with cross-functional teams to gather requirements, translate them into technical specifications, and develop solutions that align with business objectives.</li>\n<li>Develop innovative solutions to complex technical challenges utilizing modern Java frameworks and technologies.</li>\n<li>Optimize application performance through profiling, code analysis, and continuous improvement initiatives.</li>\n<li>Conduct code reviews, uphold code quality standards, and follow established development methodologies.</li>\n<li>Stay abreast of evolving Java technologies and best practices, contributing actively to the team's knowledge sharing and professional development.</li>\n</ul>\n<p><strong>Required Qualifications:</strong></p>\n<ul>\n<li>Minimum of 2 years of hands-on experience developing Java applications.</li>\n<li>In-depth knowledge of Java programming language, including core concepts, object-oriented principles, and design patterns.</li>\n<li>Thorough understanding of software development lifecycle (SDLC), agile methodologies, and version control systems (e.g., Git).</li>\n<li>Familiarity with contemporary Java frameworks, including Spring Boot, Spring MVC, Hibernate, and JPA.</li>\n<li>Experience with cloud computing platforms (e.g., AWS, GCP) is highly desirable.</li>\n</ul>\n<p><strong>Preferred Qualifications:</strong></p>\n<ul>\n<li>Experience in distributed systems, microservices architecture, and cloud-native development.</li>\n<li>Knowledge of object-relational mapping (ORM) tools (e.g., Hibernate, EclipseLink).</li>\n<li>Familiarity with continuous integration (CI) and continuous delivery (CD) pipelines.</li>\n<li>Strong analytical, problem-solving, and communication skills.</li>\n<li>Excellent teamwork, adaptability, and ability to meet demanding deadlines.</li>\n</ul>\n<p><strong>Additional Information:</strong></p>\n<ul>\n<li>Bachelor's or Master's degree in Computer Science, Software Engineering, or a related field is preferred.</li>\n<li>Candidates with strong academic credentials and involvement in technology projects are highly encouraged to apply.</li>\n<li>We offer a competitive compensation and benefits package, including health insurance, paid time off, and professional development opportunities.</li>\n</ul>\n<p><strong>To Apply:</strong></p>\n<p>Interested candidates are invited to submit their resume and a cover letter highlighting their relevant experience and skills to [email protected]</p>\n<p><strong>Please Note:</strong></p>\n<ul>\n<li>Only qualified candidates will be contacted for interviews.</li>\n<li>Applications must contain a minimum of 2+ years of experience developing Java applications.</li>\n<li>The total character count of this job description, including spaces and special characters, is approximately 3700.</li>\n</ul>"
description = """
Job Description
Job Title: Automation Tester

Job Description:

We seek a highly skilled Automation Tester to join our team and drive the development and execution of automated testing solutions. The ideal candidate will possess a deep understanding of automation principles, programming languages, and industry best practices.

Key Responsibilities:

Design, develop, and maintain automated test scripts using a variety of programming languages and frameworks (e.g., Python, Java, Selenium, Appium)
Utilize agile methodologies to automate test processes, ensuring efficient and iterative testing
Collaborate with cross-functional teams to define testing requirements and develop test plans
Execute automated tests across multiple platforms and devices
Analyze test results, identify defects, and provide detailed bug reports
Participate in test design reviews and provide feedback on test case design and coverage
Stay abreast of industry trends and best practices in automation testing
Qualifications:

Bachelor's or Master's degree in Computer Science, Software Engineering, or a related field
Minimum of 3+ years of experience in software testing, with a focus on automation
Proficient in at least one programming language commonly used in automation testing (e.g., Python, Java)
Working knowledge of web application testing frameworks (e.g., Selenium, Cypress) and mobile testing frameworks (e.g., Appium)
Strong understanding of agile development methodologies
Excellent analytical and problem-solving abilities
Ability to work independently and as part of a team
Excellent communication and interpersonal skills
"""

def main():
    extract_features_from_jd(text = description)

if __name__ == '__main__':
    main()