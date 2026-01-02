import os
import requests

api_key = os.getenv("HUGGING_FACE_API_KEY")

if not api_key:
    print("Error: HUGGING_FACE_API_KEY environment variable not set")
    exit(1)

API_URL = "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
headers = {"Authorization": f"Bearer {api_key}"}

def analyze_resume(resume_text):
    """Send resume to Hugging Face API for analysis"""
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
    
    # Call Hugging Face API
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt, "parameters": {"max_length": 1024}}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        exit(1)
    
    result = response.json()
    
    # Extract text
    if isinstance(result, list) and len(result) > 0:
        generated_text = result[0].get("generated_text", "")
        if prompt in generated_text:
            analysis = generated_text.replace(prompt, "").strip()
        else:
            analysis = generated_text.strip()
        return analysis
    else:
        return str(result)

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