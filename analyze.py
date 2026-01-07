import requests
import sys
import pdfplumber

OLLAMA_URL = "http://localhost:11434/api/generate"

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Reading PDF ... ({len(pdf.pages)} pages)\n")
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found")
        print("Make sure your PDF is in the same folder as this script")
        exit(1)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        exit(1)

def analyze_resume(resume_text):
    """Send resume to Ollama for analysis"""
    # Create prompt for analysis
    prompt = f"""Analyze this resume and provide:
1. Overall score (0-100)
2. Key strengths (3-5 points)
3. Areas for improvement (3-5 points)
4. Missing sections
5. Top 3 action items

Resume:
{resume_text}

Analysis:"""
    
    # Call Ollama 
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    
    # Error Handling
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        exit(1)
    
    result = response.json()
    return result.get("response", "")
    

if __name__ == "__main__":
    print("=" * 50)
    print("RESUME ANALYZER - Ollama")
    print("=" * 50)

    # Check if there is a valid PDF
    if len(sys.argv) > 1:
       pdf = sys.argv[1]
       print(f"\nAnalyzing: {pdf}\n")
       resume_text = extract_text_from_pdf(pdf)
    # Response if no PDF provided
    else:
       print("\nNo resume provided")
       print("Drag the PDF into the same folder as this script")
       exit(1)
    
    print("Analyzing resume ...\n")

    analysis = analyze_resume(resume_text)
    print(analysis)

    print("\n" + "=" * 50)
    print("END OF ANALYSIS")