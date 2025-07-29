#!/usr/bin/env python3
"""
Deployment setup script for PDF Preprocessor
This script helps set up the environment for deployment
"""

import os
import json
import tempfile
from pathlib import Path

def create_directories():
    """Create necessary directories for the application"""
    directories = ['images', 'temp_images']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'VISION_CREDENTIALS_PATH',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✓ All required environment variables are set")
    return True

def validate_credentials_file():
    """Validate that the credentials file exists and is valid JSON"""
    credentials_path = os.getenv('VISION_CREDENTIALS_PATH')
    if not credentials_path:
        print("❌ VISION_CREDENTIALS_PATH not set")
        return False
    
    # Check if it's a file path
    if os.path.exists(credentials_path):
        try:
            with open(credentials_path, 'r') as f:
                json.load(f)
            print(f"✓ Valid credentials file: {credentials_path}")
            return True
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in credentials file: {credentials_path}")
            return False
    else:
        # Check if it's JSON content
        try:
            json.loads(credentials_path)
            print("✓ Valid JSON credentials content")
            return True
        except json.JSONDecodeError:
            print("❌ VISION_CREDENTIALS_PATH is neither a valid file path nor JSON content")
            return False

def main():
    """Main setup function"""
    print("🔧 Setting up PDF Preprocessor for deployment...")
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed. Please set all required variables.")
        return False
    
    # Validate credentials
    if not validate_credentials_file():
        print("\n❌ Credentials validation failed.")
        return False
    
    print("\n✅ Deployment setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Ensure your environment variables are set in your deployment platform")
    print("2. For VISION_CREDENTIALS_PATH, you can either:")
    print("   - Set it to a file path (for local development)")
    print("   - Set it to the JSON content directly (for cloud deployment)")
    print("3. Deploy your application")
    
    return True

if __name__ == "__main__":
    main() 