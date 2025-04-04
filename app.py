from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import requests
import json

app = Flask(__name__)
# Enable CORS for all origins for simplicity, or restrict it later
# Allow requests from your GitHub Pages URL
CORS(app, resources={r"/process": {"origins": "https://billo-w.github.io"}})

api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = "2024-02-01" 
model_name = "gpt-4o"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    data = request.json
    input_text = data.get('text', '')
    summarize = data.get('summarize', False)
    
    result = input_text  # Default is just the original text
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
    
    # Create prompt for summarization
    system_message = """You are an AI assistant specialized in helping dyslexic learners. 
    Your task is to summarize text in a clear, concise way that is easy to read and understand for people with dyslexia.
    Use simple language, short sentences, and clear structure."""
    
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
            f"{api_endpoint}/openai/deployments/{model_name}/chat/completions?api-version={api_version}",
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
