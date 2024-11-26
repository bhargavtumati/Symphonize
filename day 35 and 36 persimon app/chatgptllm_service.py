import openai

# Set your API key
openai.api_key = "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"

def ask_chatgpt(prompt: str):
    try:
        response = openai.completions.create(  # Updated API method
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=500
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

