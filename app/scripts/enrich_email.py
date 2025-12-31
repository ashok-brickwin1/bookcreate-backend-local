#!/usr/bin/env python3
"""
Helper script to enrich email addresses with LinkedIn and other data using Enrich.so API
"""
import os
import sys
import subprocess
import requests
import time
import json
from dotenv import load_dotenv

def get_venv_python():
    """Get the Python executable from the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        return os.path.join("venv", "bin", "python")

def ensure_venv():
    """Ensure virtual environment exists and is set up"""
    venv_path = "venv"
    python_exe = get_venv_python()
    
    if not os.path.exists(venv_path):
        print("🔧 Virtual environment not found. Setting up...")
        try:
            subprocess.run([sys.executable, "scripts/setup_venv.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup virtual environment: {e}")
            return False
    
    if not os.path.exists(python_exe):
        print(f"❌ Python executable not found at {python_exe}")
        return False
    
    return True

def import_pandas():
    """Import pandas using the virtual environment"""
    if not ensure_venv():
        return None
    
    python_exe = get_venv_python()
    try:
        # Use subprocess to run pandas import in the venv
        result = subprocess.run([python_exe, "-c", "import pandas as pd; print('pandas available')"], 
                              capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Load environment variables
load_dotenv()

def get_enrich_so_data(email):
    """Get enriched data from Enrich.so API for a given email"""
    api_token = os.getenv("ENRICH_SO_API_KEY")
    
    if not api_token:
        return {'error': 'ENRICH_SO_API_KEY not found in environment variables'}
    
    payload = {'email': email}
    headers = {
        'accept': 'application/json', 
        'authorization': f'Bearer {api_token}'
    }
    
    try:
        resp = requests.get('https://api.enrich.so/v1/api/person', 
                          params=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            
            # Extract all possible fields
            enriched_data = {
                "email": email,
                "full_name": result.get("displayName"),
                "first_name": result.get("firstName"),
                "last_name": result.get("lastName"),
                "linkedin": result.get("linkedInUrl"),
                "company": result.get("company", {}).get("name"),
                "company_website": result.get("company", {}).get("website"),
                "company_industry": result.get("company", {}).get("industry"),
                "company_size": result.get("company", {}).get("staff_count"),
                "job_title": result.get("jobTitle"),
                "location": result.get("location"),
                "twitter": result.get("social", {}).get("twitter"),
                "facebook": result.get("social", {}).get("facebook"),
                "github": result.get("social", {}).get("github"),
                "phone": result.get("phone"),
                "additional_emails": ", ".join(result.get("emails", [])) if result.get("emails") else None,
                "skills": ", ".join(result.get("skills", [])) if result.get("skills") else None,
                "education": ", ".join([edu.get("name", "") for edu in result.get("education", [])]) if result.get("education") else None,
                "experience": ", ".join([exp.get("title", "") + " at " + exp.get("company", "") for exp in result.get("experience", [])]) if result.get("experience") else None,
                "success": True
            }
            return enriched_data
        else:
            return {
                'email': email, 
                'error': f'API Error {resp.status_code}: {resp.text}',
                'success': False
            }
    except requests.exceptions.RequestException as e:
        return {
            'email': email, 
            'error': f'Request failed: {str(e)}',
            'success': False
        }

def enrich_single_email(email):
    """Enrich a single email address and return the data"""
    print(f"🔍 Enriching email: {email}")
    
    result = get_enrich_so_data(email)
    
    if result.get('success'):
        print(f"✅ Found data for {email}")
        if result.get('linkedin'):
            print(f"   LinkedIn: {result['linkedin']}")
        if result.get('full_name'):
            print(f"   Name: {result['full_name']}")
        if result.get('company'):
            print(f"   Company: {result['company']}")
    else:
        print(f"❌ Failed to enrich {email}: {result.get('error', 'Unknown error')}")
    
    return result

def create_csv_from_enrichment(enrichment_data, csv_path="temp_enriched.csv"):
    """Create a CSV file from enrichment data for research_script.py"""
    if not enrichment_data.get('success'):
        return None
    
    # Create CSV manually without pandas dependency
    csv_content = f"""first_name,last_name,email,linkedin,full_name,job_title,profile_picture,background_image,summary,location,industry,education,experience,skills,followers,connections
{enrichment_data.get('first_name', '')},{enrichment_data.get('last_name', '')},{enrichment_data.get('email', '')},{enrichment_data.get('linkedin', '')},{enrichment_data.get('full_name', '')},{enrichment_data.get('job_title', '')},,,{enrichment_data.get('company', '')},{enrichment_data.get('location', '')},{enrichment_data.get('company_industry', '')},{enrichment_data.get('education', '')},{enrichment_data.get('experience', '')},{enrichment_data.get('skills', '')},,"""
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    return csv_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/enrich_email.py <email_address>")
        sys.exit(1)
    
    email = sys.argv[1]
    result = enrich_single_email(email)
    
    if result.get('success'):
        print(f"\n📊 Enrichment successful!")
        print(f"Full name: {result.get('full_name', 'N/A')}")
        print(f"LinkedIn: {result.get('linkedin', 'N/A')}")
        print(f"Company: {result.get('company', 'N/A')}")
        print(f"Job title: {result.get('job_title', 'N/A')}")
        
        # Create CSV for research_script.py
        csv_path = create_csv_from_enrichment(result)
        if csv_path:
            print(f"\n📄 Created CSV file: {csv_path}")
            print("You can now use this with research_script.py for detailed LinkedIn research")
    else:
        print(f"\n❌ Enrichment failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
