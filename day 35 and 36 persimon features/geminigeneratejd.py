import requests
from fastapi import FastAPI, HTTPException
import logging
import json

# Initialize FastAPI app
app = FastAPI()

# Replace this with your actual Gemini API key
gemini_api_key = "YOUR_GEMINI_API_KEY"

# Define the endpoint for the Gemini 1.5 model
gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Set up logging to capture errors
logging.basicConfig(level=logging.INFO)

def ask_gemini(prompt: str):
    try:
        # Set the headers (Content-Type and API key)
        headers = {
            "Content-Type": "application/json"
        }

        # Define the payload with the user's prompt
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        # Log the request details
        logging.info(f"Request data: {json.dumps(data, indent=2)}")

        # Make the POST request to the Gemini API
        response = requests.post(gemini_url, headers=headers, json=data, params={"key": gemini_api_key})

        # Log the response status and body for debugging
        logging.info(f"Gemini API response status: {response.status_code}")
        logging.info(f"Response body: {response.text}")

        # Check if the request was successful
        if response.status_code == 200:
            try:
                response_json = response.json()
                # Log the entire response JSON for debugging
                logging.info(f"Response JSON: {json.dumps(response_json, indent=2)}")

                # Check if 'contents' key exists in the response
                if 'contents' in response_json:
                    return response_json['contents'][0]['parts'][0]['text'].strip()
                else:
                    # Log the entire response if 'contents' is missing
                    logging.error("The 'contents' key is missing in the response.")
                    raise HTTPException(status_code=500, detail="Unexpected response format: 'contents' key missing")
            except json.JSONDecodeError:
                logging.error("Error decoding JSON response.")
                raise HTTPException(status_code=500, detail="Error decoding JSON response.")
        else:
            # Log the error response if the status code is not 200
            logging.error(f"Gemini API error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Gemini API error: {response.text}")

    except Exception as e:
        logging.error(f"Error while calling Gemini API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# FastAPI route for getting Gemini response
@app.post("/ask_gemini/")
async def get_gemini_response(prompt: str):
    """
    Send a prompt to Gemini and get a response.
    """
    response = ask_gemini(prompt)
    return {"response": response}
