from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

# Initialize FastAPI app
app = FastAPI()

# Configure OpenAI API key
openai.api_key = "your-api-key-here"  # Replace with your actual API key

# Define request model
class OpenAIRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

# Define OpenAI interaction function
def ask_openai(prompt: str, max_tokens: int):
    try:
        # Call OpenAI API
        response = openai.Completion.create(
            model="gpt-4",  # Specify the model to use
            prompt=prompt,
            max_tokens=max_tokens
        )
        # Return the generated text
        return response['choices'][0]['text'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define FastAPI endpoint
@app.post("/ask")
def ask_openai_endpoint(request: OpenAIRequest):
    result = ask_openai(request.prompt, request.max_tokens)
    return {"response": result}

