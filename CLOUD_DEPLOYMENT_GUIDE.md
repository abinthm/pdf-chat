# 🚀 Cloud Deployment with Service Account

## **✅ Updated for Service Account Authentication**

Your code now supports both approaches:
- **Local Development**: JSON credentials file
- **Cloud Deployment**: Service account (recommended)

## **🔧 Cloud Run Configuration**

### **1. Service Account Setup**
In the "Security" tab, you have:
- **Service Account**: `ocr-pramana` (already configured)

### **2. Environment Variables**
In the "Variables & Secrets" tab, add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
```

**Note**: You don't need `VISION_CREDENTIALS_PATH` anymore! The service account handles Vision API authentication.

### **3. Service Account Permissions**
Make sure your service account has these roles:
- `Cloud Vision API User`
- `Cloud Storage Object Viewer` (if needed)

## **🎯 Benefits of Service Account Approach**

✅ **More Secure**: No JSON files to manage  
✅ **Simpler Deployment**: No credentials to upload  
✅ **Automatic Rotation**: Google manages the keys  
✅ **Better Security**: Follows cloud best practices  

## **🚀 Deployment Steps**

1. **Set Environment Variables** (without VISION_CREDENTIALS_PATH)
2. **Click "Create"** to deploy
3. **Your app will use the service account automatically**

## **🔍 How It Works**

When `VISION_CREDENTIALS_PATH` is not set:
- The app automatically uses the default service account
- Google Cloud handles authentication
- No JSON files needed

## **📝 Local Development**

For local development, you can still use JSON credentials:
```bash
VISION_CREDENTIALS_PATH=/path/to/credentials.json
```

## **🎉 You're Ready!**

Your deployment is now simpler and more secure. Just set the environment variables and deploy! 