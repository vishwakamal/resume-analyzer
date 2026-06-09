from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

CORS(app)

# Configuration
HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY', '')
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def analyze_with_huggingface(resume_text):
    """Send resume text to Hugging Face for analysis"""
    
    if not HUGGING_FACE_API_KEY:
        raise ValueError("Hugging Face API key not set in .env file")
    
    prompt = f"""Analyze this resume and provide feedback in this exact format:

SCORE: [0-100]
STRENGTHS:
- strength 1
- strength 2
- strength 3
IMPROVEMENTS:
- improvement 1
- improvement 2
- improvement 3
MISSING_SECTIONS:
- section 1
- section 2
ACTION_ITEMS:
- action 1
- action 2
- action 3

Resume:
{resume_text}"""

    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    
    # Try multiple models if one fails
    models = [
        "mistralai/Mistral-7B-Instruct-v0.1",
        "meta-llama/Llama-2-7b-chat-hf",
        "gpt2"
    ]
    
    for model in models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                else:
                    generated_text = str(result)
                
                if generated_text:
                    analysis = parse_response(generated_text)
                    return analysis
            
            elif response.status_code == 503:
                continue
            elif response.status_code == 429:
                return get_default_analysis()
            else:
                continue
                
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"Error with {model}: {str(e)}")
            continue
    
    return get_default_analysis()

def get_default_analysis():
    """Return default analysis if API fails"""
    return {
        'overall_score': 72,
        'strengths': [
            'Professional format and structure',
            'Clear presentation of experience',
            'Relevant technical skills listed'
        ],
        'improvements': [
            'Add quantifiable metrics to achievements',
            'Include action verbs in bullet points',
            'Improve spacing and formatting'
        ],
        'missing_sections': [
            'Link to portfolio or GitHub',
            'Certifications or awards'
        ],
        'action_items': [
            'Quantify your achievements with numbers and percentages',
            'Use strong action verbs (Led, Managed, Developed)',
            'Tailor resume to job description keywords'
        ]
    }

def parse_response(text):
    """Parse AI response into structured format"""
    try:
        lines = text.split('\n')
        
        # Extract score
        score = 75
        for line in lines:
            if 'SCORE:' in line:
                try:
                    score = int(''.join(filter(str.isdigit, line.split(':')[1])))
                    score = min(100, max(0, score))
                    break
                except:
                    score = 75
        
        def extract_list(section_name):
            items = []
            in_section = False
            
            for line in lines:
                if section_name in line:
                    in_section = True
                    continue
                
                if in_section:
                    line = line.strip()
                    if line.startswith('-'):
                        item = line[1:].strip()
                        if item:
                            items.append(item)
                    elif line and any(keyword in line for keyword in ['SCORE', 'STRENGTHS', 'IMPROVEMENTS', 'MISSING', 'ACTION']):
                        break
            
            return items[:5]
        
        strengths = extract_list('STRENGTHS') or ['Professional format', 'Clear structure', 'Good organization']
        improvements = extract_list('IMPROVEMENTS') or ['Add metrics', 'Improve formatting', 'Better keywords']
        missing_sections = extract_list('MISSING_SECTIONS') or ['Portfolio link', 'Certifications']
        action_items = extract_list('ACTION_ITEMS') or ['Quantify achievements', 'Use action verbs', 'Add keywords']
        
        return {
            'overall_score': score,
            'strengths': strengths[:5],
            'improvements': improvements[:5],
            'missing_sections': missing_sections[:3],
            'action_items': action_items[:3]
        }
    except Exception as e:
        print(f"Parse error: {str(e)}")
        return get_default_analysis()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze resume PDF"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Save file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(file_path)

            if not resume_text.strip():
                return jsonify({'error': 'Could not extract text from PDF'}), 400

            # Analyze with Hugging Face
            analysis = analyze_with_huggingface(resume_text)

            return jsonify(analysis), 200

        finally:
            # Clean up - always delete the file
            if os.path.exists(file_path):
                os.remove(file_path)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)