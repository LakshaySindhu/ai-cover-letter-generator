import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def index():
    """Renders the main page of the application."""
    return render_template('index.html')

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():
    """
    Handles the request to generate a cover letter using the Gemini API.
    It takes job title, company, skills, and experience from the form,
    constructs a prompt, calls the Gemini API, and returns the generated text.
    """
    job_title = request.form.get('job_title')
    company = request.form.get('company')
    skills = request.form.get('skills')
    experience = request.form.get('experience')

    if not all([job_title, company, skills, experience]):
        return jsonify({"error": "All fields are required."}), 400

    # Construct the prompt for the Gemini API
    prompt = f"""
    Write a professional and compelling cover letter for a job application.

    Job Title: {job_title}
    Company: {company}
    My Skills: {skills}
    My Experience: {experience}

    The cover letter should highlight how my skills and experience align with the job requirements and express enthusiasm for the role and company.
    """

    # Gemini API endpoint and payload
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1000
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        # Extract the generated text
        if result and result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"cover_letter": generated_text})
        else:
            return jsonify({"error": "Failed to generate cover letter. Unexpected API response."}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    # Create a 'templates' directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # app.run(debug=True) # Set debug=False in production

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
