#!/usr/bin/env python3
"""
Helper script to enhance individual research with LinkedIn data using research_script.py
"""
import os
import sys
import subprocess
import json
from pathlib import Path

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

def create_temp_csv(full_name, linkedin_url, csv_path="temp_linkedin.csv"):
    """Create a temporary CSV for single person processing"""
    first_name = full_name.split()[0] if full_name else ''
    last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
    
    csv_content = f"""first_name,last_name,email,linkedin,full_name,job_title,profile_picture,background_image,summary,location,industry,education,experience,skills,followers,connections
{first_name},{last_name},,{linkedin_url},{full_name},,,,,,,,,,"""
    
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    return csv_path

def run_linkedin_research(full_name, linkedin_url):
    """Run research_script.py for a single person with LinkedIn data"""
    
    # Ensure virtual environment is set up
    if not ensure_venv():
        return {'success': False, 'error': 'Failed to setup virtual environment'}
    
    # Create temporary CSV
    temp_csv = create_temp_csv(full_name, linkedin_url)
    
    try:
        # Run research script using venv Python
        python_exe = get_venv_python()
        print(f"🔍 Running LinkedIn research for {full_name}...")
        result = subprocess.run([python_exe, "research_script.py"], 
                              capture_output=True, text=True, check=True)
        
        # Read the generated data
        safe_name = "".join(c for c in full_name if c.isalnum() or c in (" ", "-", "_")).rstrip().replace(" ", "_")
        json_path = f"output_data/{safe_name}.json"
        txt_path = f"bios/{safe_name}.txt"
        
        linkedin_data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                linkedin_data = json.load(f)
        
        bio_text = ""
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                bio_text = f.read()
        
        return {
            'success': True,
            'linkedin_data': linkedin_data,
            'bio_text': bio_text,
            'raw_data': linkedin_data.get('external_raw_data', {}),
            'summary': linkedin_data.get('supplemental_context_summary', ''),
            'final_bio': linkedin_data.get('grok_final_bio', bio_text)
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ LinkedIn research failed: {e}")
        return {'success': False, 'error': str(e)}
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_csv):
            os.remove(temp_csv)
        if os.path.exists("output_data"):
            import shutil
            shutil.rmtree("output_data")
        if os.path.exists("bios"):
            shutil.rmtree("bios")

def enhance_bio_with_linkedin(bio_file, linkedin_data):
    """Enhance existing bio with LinkedIn data"""
    
    if not linkedin_data.get('success'):
        return bio_file
    
    # Read existing bio
    if os.path.exists(bio_file):
        with open(bio_file, 'r', encoding='utf-8') as f:
            existing_bio = f.read()
    else:
        existing_bio = ""
    
    # Get LinkedIn-enhanced bio
    linkedin_bio = linkedin_data.get('final_bio', '')
    
    # Combine or replace based on content quality
    if linkedin_bio and len(linkedin_bio) > len(existing_bio):
        enhanced_bio = f"""# Biography (Enhanced with LinkedIn Data)

{linkedin_bio}

---
*This biography has been enhanced with detailed LinkedIn profile data and professional information.*
"""
    else:
        enhanced_bio = existing_bio
    
    # Write enhanced bio
    with open(bio_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_bio)
    
    return enhanced_bio

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/linkedin_enhance.py <full_name> <linkedin_url>")
        sys.exit(1)
    
    full_name = sys.argv[1]
    linkedin_url = sys.argv[2]
    
    result = run_linkedin_research(full_name, linkedin_url)
    
    if result['success']:
        print("✅ LinkedIn research completed successfully")
        print(f"📊 Summary: {result['summary'][:200]}...")
        print(f"📝 Bio length: {len(result['final_bio'])} characters")
    else:
        print(f"❌ LinkedIn research failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
