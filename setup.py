#!/usr/bin/env python3
"""
Setup script for Company Policy RAG Assistant
"""

import os
import sys
from pathlib import Path

def setup_project():
    """Initialize project structure and dependencies"""
    print("Setting up Company Policy RAG Assistant...")
    
    # Create directories
    directories = [
        "data/policies",
        "data/processed",
        "logs",
        "tests",
        "app/models",
        "app/services",
        "app/api",
        "app/utils",
        "app/frontend/static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create sample policy files
    sample_policies = [
        ("hr_policies.txt", "HR Policy: Leave Policy\nEmployees are entitled to 20 days of annual leave per year."),
        ("leave_attendance.txt", "Leave Policy: Sick Leave\nSick leave is 10 days per year with medical certificate."),
        ("procurement_guidelines.txt", "Procurement: Purchase Approval\nAll purchases above $5000 require manager approval."),
    ]
    
    for filename, content in sample_policies:
        filepath = Path("data/policies") / filename
        if not filepath.exists():
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Created sample policy: {filename}")
    
    # Check if .env file exists
    if not Path(".env").exists():
        with open(".env", 'w') as f:
            f.write("""# Add your API keys here
NVIDIA_API_KEY=
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_PROVIDER=nvidia
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
""")
        print("Created .env file. Please add your NVIDIA API key.")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Add your API keys to .env file")
    print("2. Place your policy documents in data/policies/")
    print("3. Run: pip install -r requirements.txt")
    print("4. Run: python app/main.py")
    print("5. Open browser: http://localhost:8000/docs")
    print("6. For frontend: streamlit run app/frontend/streamlit_app.py")

if __name__ == "__main__":
    setup_project()