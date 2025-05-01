from app.helpers import classifier_helper as classifierh
from app.core.config import settings
from google.generativeai import GenerativeModel, configure
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from tenacity import retry, wait_fixed, stop_after_attempt
import os
import asyncio
import threading

configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = GenerativeModel(os.getenv("GENAI"))
API_KEYS = [
    os.getenv("KEY_1"),
    os.getenv("KEY_2"),
    os.getenv("KEY_3"),
    os.getenv("KEY_4")
]

semaphores = {key: asyncio.Semaphore(15) for key in API_KEYS}
semaphore_locks = {key: threading.Lock() for key in API_KEYS}
rate_reset_interval = 60  

api_key_cycle = cycle(API_KEYS)
executor = ThreadPoolExecutor()

def get_match_score(job_description: str, resume_text: str):
    classifierh.run_once()
    message = job_description + " " + resume_text
    result, probs = classifierh.classify_message(message=message, model_version=settings.CLASSIFIER_VERSION, vectorizer_version=settings.VECTORIZER_VERSION)

    match_score = str(round(probs[classifierh.get_class_key(result)] * 100, 2))
    
    probabilities = []
    
    for i, prob in enumerate(probs):
        probabilities.append(
            {
                "label": classifierh.class_labels[i],
                "probability": round(float(prob), 4)
            }
        )

    match = {
        "result": result,
        "score": match_score,
        "probabilities": probabilities
    }
    
    return match

async def calculate_match_percentage(resume_text, jd_text):
    prompt = f"""
    Analyze the following resume and job description, and calculate the match percentage based on skills, experience, and relevance.
    Resume: {resume_text}
    Job Description: {jd_text}
    Respond with only the match percentage as a whole number ranging from 0 to 100 (e.g., 32 for 32%).
    """
    try:
        response = gemini_model.generate_content(prompt)
        print(f"the response is {response.text.strip()}")
        return int(response.text.strip())
    except Exception as e:
        return 0  

async def reset_semaphores():
    while True:
        await asyncio.sleep(rate_reset_interval)
        for key in API_KEYS:
            semaphores[key] = asyncio.Semaphore(15)

def get_model_for_key(api_key):
    configure(api_key=api_key)
    return gemini_model


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
async def calculate_match_percentage_concurrently(resume, jd_text, feedback):
    api_key = next(api_key_cycle)
    semaphore = semaphores[api_key]

    async with semaphore:
        prompt = f"""
        You are a job-matching AI evaluating how well a resume aligns with a job description.

        The job description may emphasize certain technologies (like Java), but the user has provided specific feedback that MUST influence your scoring.

        Resume:
        {resume['text']}

        Job Description:
        {jd_text}

        Important User Feedback:
        {feedback}

        Apply this feedback **strictly** when scoring. For example, if the feedback says to prioritize Android developers—even over the JD requirements—you must score Android-focused candidates higher, even if the JD mentions Java more.

        Now, return only a single integer match percentage (0 to 100) that reflects this customized logic. No extra text.
        """
        loop = asyncio.get_event_loop()

        try:
            model = await loop.run_in_executor(executor, get_model_for_key, api_key)
            response = await loop.run_in_executor(executor, model.generate_content, prompt)
            score = int(response.text.strip())
            resume['doc']['persimmon_score'] = score
            return resume
        except Exception as e:
            return {"error": str(e)}


async def process_in_batches(resumes, jd_text, feedback, batch_size=60):
    results = []
    asyncio.create_task(reset_semaphores())

    for i in range(0, len(resumes), batch_size):
        batch = resumes[i:i + batch_size]
        tasks = [calculate_match_percentage_concurrently(resume, jd_text, feedback) for resume in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

        if i + batch_size < len(resumes):
            await asyncio.sleep(rate_reset_interval)

    return results
