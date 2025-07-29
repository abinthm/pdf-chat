# 🚀 Simple Google Cloud Run Deployment Guide

## **For Complete Beginners - No Docker/Cloud Experience Required!**

This guide will take you from zero to deployed app in 30 minutes! 🎯

---

## **Step 1: Install Required Tools (5 minutes)**

### 1.1 Install Google Cloud CLI
- Go to: https://cloud.google.com/sdk/docs/install
- Download the installer for Windows
- Run the installer and follow the prompts
- **Restart your computer** after installation

### 1.2 Install Docker Desktop
- Go to: https://docs.docker.com/get-docker/
- Download Docker Desktop for Windows
- Run the installer and follow the prompts
- **Restart your computer** after installation

---

## **Step 2: Set Up Google Cloud (10 minutes)**

### 2.1 Create Google Cloud Account
- Go to: https://console.cloud.google.com
- Sign in with your Google account
- Create a new project (or use existing)

### 2.2 Enable Required APIs
In Google Cloud Console, search for and enable these APIs:
1. **Cloud Run API**
2. **Cloud Build API** 
3. **Vision API**

### 2.3 Get Your Project ID
- In Google Cloud Console, note your **Project ID** (you'll need this later)
- It looks like: `my-project-123456`

---

## **Step 3: Get Your API Keys (5 minutes)**

### 3.1 Supabase Keys
1. Go to your Supabase project dashboard
2. Go to Settings → API
3. Copy:
   - **Project URL** (looks like: `https://abc123.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

### 3.2 Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

---

## **Step 4: Deploy Your App (10 minutes)**

### 4.1 Open Command Prompt
- Press `Windows + R`
- Type `cmd` and press Enter
- Navigate to your project folder:
```bash
cd C:\Users\abinv\Desktop\DEV\pdfas\pdfprepro
```

### 4.2 Login to Google Cloud
```bash
gcloud auth login
```
- A browser window will open
- Sign in with your Google account
- Allow permissions

### 4.3 Set Your Project
```bash
gcloud config set project YOUR_PROJECT_ID
```
(Replace `YOUR_PROJECT_ID` with your actual project ID)

### 4.4 Run the Deployment Script
```bash
python deploy_to_cloud_run.py
```

The script will ask you for:
- Your Supabase URL
- Your Supabase API key  
- Your Gemini API key
- Your Google Cloud Project ID
- Service name (just press Enter for default)
- Region (just press Enter for default)

---

## **Step 5: Test Your App (5 minutes)**

### 5.1 Get Your App URL
After deployment, you'll see a URL like:
```
https://pdfprepro-YOUR_PROJECT_ID.run.app
```

### 5.2 Test the App
1. Open the URL in your browser
2. You should see: `{"message": "PDF Chatbot Backend API", "version": "1.0.0"}`
3. If you see this, your app is working! 🎉

---

## **🎯 What Just Happened?**

1. **Google Cloud CLI** - Lets you control Google Cloud from your computer
2. **Docker** - Packages your app so it can run anywhere
3. **Cloud Run** - Google's service that runs your app in the cloud
4. **Environment Variables** - Your API keys and settings
5. **Deployment** - Uploading your app to Google's servers

---

## **🐛 Troubleshooting**

### "gcloud not found"
- Restart your computer after installing Google Cloud CLI
- Or run: `C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`

### "Docker not found"
- Restart your computer after installing Docker Desktop
- Make sure Docker Desktop is running (check system tray)

### "Permission denied"
- Run Command Prompt as Administrator

### "Project not found"
- Make sure you're using the correct Project ID
- Check that you're logged in: `gcloud auth list`

### "API not enabled"
- Go to Google Cloud Console
- Enable the required APIs (Cloud Run, Cloud Build, Vision)

---

## **📞 Need Help?**

1. **Check the logs**: `gcloud run logs read --region=us-central1`
2. **Redeploy**: Run the script again
3. **Google Cloud Console**: Check your project at console.cloud.google.com

---

## **🎉 You're Done!**

Your PDF Preprocessor is now running in the cloud! You can:
- Upload PDFs from anywhere
- Process them with AI
- Access your app 24/7

**Next time you want to update your app, just run the deployment script again!** 