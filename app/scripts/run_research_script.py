#!/usr/bin/env python3
"""
Helper script to run research_script.py with workflow integration
"""
import os
import sys
import subprocess
import json
import shutil
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

def run_research_script(csv_file="input_people.csv", output_dir="research/batch"):
    """Run research_script.py and organize outputs"""
    
    # Ensure virtual environment is set up
    if not ensure_venv():
        return False
    
    # Ensure CSV exists
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/raw_data", exist_ok=True)
    os.makedirs(f"{output_dir}/biographies", exist_ok=True)
    
    print(f"🔍 Running research_script.py with {csv_file}...")
    
    # Run the research script using venv Python
    python_exe = get_venv_python()
    try:
        result = subprocess.run([python_exe, "research_script.py"], 
                              capture_output=True, text=True, check=True)
        print("✅ Research script completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Research script failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Organize outputs
    print("📁 Organizing outputs...")
    
    # Move JSON files
    if os.path.exists("output_data"):
        for json_file in Path("output_data").glob("*.json"):
            dest_path = Path(f"{output_dir}/raw_data") / json_file.name
            try:
                if dest_path.exists():
                    dest_path.unlink()
                shutil.move(str(json_file), str(dest_path))
            except Exception as e:
                print(f"⚠️  Skipped moving {json_file} -> {dest_path}: {e}")
        print(f"📄 Moved JSON files to {output_dir}/raw_data/")
    
    # Move TXT biographies
    if os.path.exists("bios"):
        for txt_file in Path("bios").glob("*.txt"):
            dest_path = Path(f"{output_dir}/biographies") / txt_file.name
            try:
                if dest_path.exists():
                    dest_path.unlink()
                shutil.move(str(txt_file), str(dest_path))
            except Exception as e:
                print(f"⚠️  Skipped moving {txt_file} -> {dest_path}: {e}")
        print(f"📝 Moved biographies to {output_dir}/biographies/")
    
    # Generate summary report
    generate_summary_report(csv_file, output_dir)
    
    return True

def generate_summary_report(csv_file, output_dir):
    """Generate a summary report of the batch processing"""
    
    summary_path = f"{output_dir}/batch_summary.md"
    
    # Count processed files
    raw_data_count = len(list(Path(f"{output_dir}/raw_data").glob("*.json")))
    bio_count = len(list(Path(f"{output_dir}/biographies").glob("*.txt")))
    
    # Read CSV to get person names
    import pandas as pd
    try:
        df = pd.read_csv(csv_file)
        person_names = df['full_name'].tolist() if 'full_name' in df.columns else []
    except:
        person_names = ["Unknown"]
    
    # Generate summary
    summary_content = f"""# Batch Research Summary

## Overview
- **CSV File**: {csv_file}
- **Processed**: {raw_data_count} people
- **Biographies Generated**: {bio_count}
- **Output Directory**: {output_dir}

## Processed People
{chr(10).join(f"- {name}" for name in person_names)}

## Output Structure
```
{output_dir}/
├── raw_data/          # JSON files with detailed research data
├── biographies/       # TXT files with final biographies
└── batch_summary.md   # This summary file
```

## Next Steps
1. Review individual biographies in `biographies/` directory
2. Check detailed data in `raw_data/` directory
3. Use individual research files for book outline generation
4. Integrate findings into your book project

## Integration with Book Workflows
You can now use these research files with the existing book workflows:
- Individual biographies can be used for character research
- Raw data can inform chapter development
- Themes and patterns can be extracted for book structure
"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"📊 Generated summary report: {summary_path}")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "input_people.csv"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "research/batch"
    
    success = run_research_script(csv_file, output_dir)
    sys.exit(0 if success else 1)
