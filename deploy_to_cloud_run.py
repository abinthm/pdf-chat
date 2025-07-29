#!/usr/bin/env python3
"""
Simple Google Cloud Run Deployment Script
This script helps you deploy your PDF Preprocessor to Google Cloud Run
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def read_credentials_file():
    """Read the credentials file and return its content"""
    credentials_file = "gen-lang-client-0250729981-f4854d1a53eb.json"
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as f:
            return json.dumps(json.load(f))
    else:
        print(f"❌ Credentials file not found: {credentials_file}")
        return None

def create_env_file():
    """Create a .env.yaml file for Cloud Run deployment"""
    print("🔧 Creating environment configuration...")
    
    # Read credentials
    credentials_json = read_credentials_file()
    if not credentials_json:
        return False
    
    # Get environment variables from user
    print("\n📝 Please provide your environment variables:")
    print("(You can find these in your Supabase project settings)")
    
    supabase_url = input("Enter your SUPABASE_URL: ").strip()
    supabase_key = input("Enter your SUPABASE_KEY: ").strip()
    gemini_api_key = input("Enter your GEMINI_API_KEY: ").strip()
    
    if not all([supabase_url, supabase_key, gemini_api_key]):
        print("❌ All environment variables are required!")
        return False
    
    # Create .env.yaml file
    env_content = f"""SUPABASE_URL: "{supabase_url}"
SUPABASE_KEY: "{supabase_key}"
GEMINI_API_KEY: "{gemini_api_key}"
VISION_CREDENTIALS_PATH: '{credentials_json}'
"""
    
    with open('.env.yaml', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.yaml file")
    return True

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check if gcloud is installed
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI is installed")
        else:
            print("❌ Google Cloud CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI not installed")
        print("📥 Download from: https://cloud.google.com/sdk/docs/install")
        return False
    
    # Check if Docker is installed
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed")
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        print("📥 Download from: https://docs.docker.com/get-docker/")
        return False
    
    return True

def deploy_to_cloud_run():
    """Deploy the application to Google Cloud Run"""
    print("\n🚀 Starting deployment to Google Cloud Run...")
    
    # Get project ID
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required!")
        return False
    
    # Get service name
    service_name = input("Enter service name (default: pdfprepro): ").strip() or "pdfprepro"
    
    # Get region
    region = input("Enter region (default: us-central1): ").strip() or "us-central1"
    
    print(f"\n📋 Deployment Configuration:")
    print(f"  Project ID: {project_id}")
    print(f"  Service Name: {service_name}")
    print(f"  Region: {region}")
    
    confirm = input("\nProceed with deployment? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Deployment cancelled")
        return False
    
    # Build and deploy
    try:
        print("\n🔨 Building and deploying...")
        cmd = [
            'gcloud', 'run', 'deploy', service_name,
            '--source', '.',
            '--region', region,
            '--project', project_id,
            '--env-vars-file', '.env.yaml',
            '--allow-unauthenticated',
            '--memory', '2Gi',
            '--cpu', '2',
            '--timeout', '3600'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n✅ Deployment successful!")
            print(f"🌐 Your app is now running at: https://{service_name}-{project_id}.run.app")
            return True
        else:
            print("❌ Deployment failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        return False

def main():
    """Main deployment function"""
    print("🚀 PDF Preprocessor - Google Cloud Run Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Please install the required tools and try again.")
        return False
    
    # Create environment file
    if not create_env_file():
        print("\n❌ Failed to create environment configuration.")
        return False
    
    # Deploy to Cloud Run
    if not deploy_to_cloud_run():
        print("\n❌ Deployment failed.")
        return False
    
    print("\n🎉 Congratulations! Your app is now deployed!")
    print("\n📝 Next steps:")
    print("1. Test your app by visiting the URL provided")
    print("2. Upload a PDF and test the functionality")
    print("3. Monitor logs in Google Cloud Console")
    
    return True

if __name__ == "__main__":
    main() 