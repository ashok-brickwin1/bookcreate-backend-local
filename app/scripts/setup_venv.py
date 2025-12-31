#!/usr/bin/env python3
"""
Setup virtual environment and install dependencies for research_script.py
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def create_venv(venv_path="venv"):
    """Create virtual environment if it doesn't exist"""
    if not os.path.exists(venv_path):
        print(f"🔧 Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
    else:
        print(f"✅ Virtual environment already exists at {venv_path}")
    
    return venv_path

def get_python_executable(venv_path="venv"):
    """Get the Python executable path for the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux/macOS
        return os.path.join(venv_path, "bin", "python")

def install_dependencies(venv_path="venv"):
    """Install required dependencies in the virtual environment"""
    python_exe = get_python_executable(venv_path)
    
    # Required packages for research_script.py
    packages = [
        "requests",
        "pandas", 
        "python-dotenv",
        "openai",
        "tenacity"
    ]
    
    print("📦 Installing dependencies...")
    for package in packages:
        try:
            subprocess.run([python_exe, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed successfully")
    return True

def setup_environment():
    """Complete setup: create venv and install dependencies"""
    venv_path = create_venv()
    success = install_dependencies(venv_path)
    
    if success:
        python_exe = get_python_executable(venv_path)
        print(f"\n🎉 Setup complete!")
        print(f"Virtual environment: {venv_path}")
        print(f"Python executable: {python_exe}")
        print(f"\nTo activate manually: source {venv_path}/bin/activate")
        return True
    else:
        print("❌ Setup failed")
        return False

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
