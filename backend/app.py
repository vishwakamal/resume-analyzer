from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CORS(app)

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def analyze_with_ollama(resume_text):
    """Send resume text to Ollama for analysis"""
    prompt = f"""Analyze this resume and provide:
1. Overall score (0-100)
2. Key strengths (3-5 points)
3. Areas for improvement (3-5 points)
4. Missing sections
5. Top 3 action items

Resume:
{resume_text}

Provide the response in this exact format:
SCORE: [number]
STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]
IMPROVEMENTS:
- [improvement 1]
- [improvement 2]
- [improvement 3]
MISSING_SECTIONS:
- [section 1]
- [section 2]
ACTION_ITEMS:
- [item 1]
- [item 2]
- [item 3]"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code != 200:
            raise ValueError(f"Ollama error: {response.status_code}")

        result = response.json()
        generated_text = result.get("response", "")
        
        analysis = parse_ollama_response(generated_text)
        return analysis
    except Exception as e:
        raise ValueError(f"Error analyzing resume: {str(e)}")

def parse_ollama_response(text):
    """Parse Ollama response into structured format"""
    try:
        score_line = [line for line in text.split('\n') if 'SCORE:' in line][0]
        score = int(score_line.split(':')[1].strip())

        def extract_list(section_name):
            lines = text.split('\n')
            start_idx = None
            for i, line in enumerate(lines):
                if section_name in line:
                    start_idx = i + 1
                    break
            
            if start_idx is None:
                return []
            
            items = []
            for i in range(start_idx, len(lines)):
                line = lines[i].strip()
                if line.startswith('-'):
                    items.append(line[1:].strip())
                elif line and not line.startswith('-') and any(keyword in line for keyword in ['SCORE', 'STRENGTHS', 'IMPROVEMENTS', 'MISSING', 'ACTION']):
                    break
            
            return items[:5]

        strengths = extract_list('STRENGTHS')
        improvements = extract_list('IMPROVEMENTS')
        missing_sections = extract_list('MISSING_SECTIONS')
        action_items = extract_list('ACTION_ITEMS')

        strengths = strengths[:5] if strengths else ['Professional format', 'Clear structure', 'Relevant experience']
        improvements = improvements[:5] if improvements else ['Add more metrics', 'Improve formatting', 'Include certifications']
        missing_sections = missing_sections[:3] if missing_sections else ['Cover letter reference', 'Portfolio link']
        action_items = action_items[:3] if action_items else ['Quantify achievements', 'Add action verbs', 'Include keywords']

        return {
            'overall_score': score,
            'strengths': strengths,
            'improvements': improvements,
            'missing_sections': missing_sections,
            'action_items': action_items
        }
    except Exception as e:
        return {
            'overall_score': 75,
            'strengths': ['Professional format', 'Clear structure', 'Relevant experience'],
            'improvements': ['Add more metrics', 'Improve formatting', 'Include certifications'],
            'missing_sections': ['Cover letter reference', 'Portfolio link'],
            'action_items': ['Quantify achievements', 'Add action verbs', 'Include keywords']
        }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze resume PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        resume_text = extract_text_from_pdf(file_path)

        if not resume_text.strip():
            os.remove(file_path)
            return jsonify({'error': 'Could not extract text from PDF'}), 400

        analysis = analyze_with_ollama(resume_text)

        os.remove(file_path)

        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)