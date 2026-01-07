import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

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
   # Sample resume to test
   sample_resume = """
   JOHN DOE
   john@email.com | (555) 123-4567
  
   EXPERIENCE
   Senior Software Engineer at TechCorp (2020-2024)
   - Led team of 5 developers
   - Improved system performance by 40%
   - Built REST APIs serving 1M+ requests daily
  
   EDUCATION
   BS Computer Science, State University (2020)
  
   SKILLS
   Python, JavaScript, React, AWS, SQL, Git
   """
  
   print("=" * 50)
   print("RESUME ANALYZER")
   print("=" * 50)
   print("\nAnalyzing resume...\n")
  
   analysis = analyze_resume(sample_resume)
   print(analysis)
  
   print("\n" + "=" * 50)
   print("END OF ANALYSIS")