#!/usr/bin/env python3
"""
Script to help create a new Google Cloud service account for Vision API
"""

import subprocess
import json
import os

def check_gcloud_auth():
    """Check if user is authenticated with gcloud"""
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
        if 'ACTIVE' in result.stdout:
            print("✅ Google Cloud CLI is authenticated")
            return True
        else:
            print("❌ Not authenticated with Google Cloud CLI")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI not found")
        return False

def create_service_account():
    """Create a new service account for Vision API"""
    print("🔧 Creating new service account for Vision API...")
    
    # Get project ID
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], capture_output=True, text=True)
        project_id = result.stdout.strip()
        if not project_id:
            print("❌ No project set. Please run: gcloud config set project YOUR_PROJECT_ID")
            return False
        print(f"✅ Using project: {project_id}")
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return False
    
    # Create service account
    service_account_name = "pdf-vision-api"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    print(f"Creating service account: {service_account_email}")
    
    try:
        # Create service account
        subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'create', service_account_name,
            '--display-name', 'PDF Vision API Service Account',
            '--description', 'Service account for PDF Vision API processing'
        ], check=True)
        print("✅ Service account created")
        
        # Grant Vision API role
        subprocess.run([
            'gcloud', 'projects', 'add-iam-policy-binding', project_id,
            '--member', f'serviceAccount:{service_account_email}',
            '--role', 'roles/ml.developer'
        ], check=True)
        print("✅ Vision API role granted")
        
        # Create and download key
        key_file = f"{service_account_name}-key.json"
        subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create', key_file,
            '--iam-account', service_account_email
        ], check=True)
        print(f"✅ Service account key created: {key_file}")
        
        # Rename to match expected filename
        target_file = "gen-lang-client-0250729981-f4854d1a53eb.json"
        if os.path.exists(key_file):
            os.rename(key_file, target_file)
            print(f"✅ Renamed to: {target_file}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating service account: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Google Cloud Vision API Service Account Setup")
    print("=" * 50)
    
    # Check authentication
    if not check_gcloud_auth():
        print("\n📝 Please authenticate first:")
        print("gcloud auth login")
        return False
    
    # Create service account
    if create_service_account():
        print("\n✅ Service account setup completed!")
        print("\n📝 Next steps:")
        print("1. The credentials file is now available")
        print("2. You can deploy your application")
        print("3. The file is already in .gitignore (won't be committed)")
        return True
    else:
        print("\n❌ Service account setup failed")
        return False

if __name__ == "__main__":
    main() 