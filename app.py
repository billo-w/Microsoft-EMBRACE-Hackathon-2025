from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import requests
import json

app = Flask(__name__)

CORS(app, resources={r"/process": {"origins": "https://dyslexiahelper.uk"}})

api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_VERSION")
model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

@app.route('/')
def index():
    return render_template('index.html')

MAX_INPUT_LENGTH = 10000

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    input_text = data.get('text', '')
    summarize = data.get('summarize', False)

    if len(input_text) > MAX_INPUT_LENGTH:
        return jsonify({"error": "Input text too long."}), 413
    
    result = input_text  
    summary = None
    
    if summarize:
        summary = generate_summary(input_text)
    
    return jsonify({
        'original_text': input_text,
        'processed_text': result,
        'summary': summary
    })

def generate_summary(text):
    """Generate a summary of the provided text using Azure OpenAI GPT-4o"""
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    system_message = """You are an expert AI assistant transforming text into highly readable summaries for individuals with dyslexia. Your primary goal is clarity and ease of reading. Please summarize the provided text following these specific instructions:

* **Core Task:** Provide a concise summary, capturing the main points accurately.
* **Language Style:** Use simple, everyday vocabulary. Employ active voice whenever possible. Keep sentences short, clear, and direct (ideally under 15 words).
* **Formatting for Readability:**
    * Break text into short paragraphs (max 2-3 sentences each). Ensure generous spacing between paragraphs (output as separate paragraphs).
    * Utilize bullet points (`* `) or numbered lists (`1. `) frequently to present information clearly, especially for lists, steps, or key features.
    * Use **bold text** strategically and sparingly to emphasize essential terms or main ideas. Do *not* use italics or underlining.
* **Output Format:** Generate the output using standard Markdown formatting for lists and bold text.
* **Overall Tone:** Maintain a helpful and direct tone."""
    
    payload = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Please summarize the following text in a way that's accessible for dyslexic readers: {text}"}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(
            f"{api_endpoint.strip('/')}/openai/deployments/{model_name}/chat/completions?api-version={api_version}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Error generating summary. Please try again."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port) 
