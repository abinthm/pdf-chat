# Deployment Guide for PDF Preprocessor

## 🚨 Critical Issues Fixed

The following deployment issues have been resolved:

1. **VISION_CREDENTIALS_PATH handling** - Now supports both file paths and JSON content
2. **Environment variable validation** - All required variables are now validated
3. **Docker health check** - Added curl installation for proper health checks
4. **Volume permissions** - Added read-write permissions for Docker volumes

## 📋 Prerequisites

Before deploying, ensure you have:

- [ ] Google Cloud Vision API credentials
- [ ] Supabase project URL and API key
- [ ] Gemini API key
- [ ] Docker installed (for containerized deployment)

## 🔧 Environment Variables

Set the following environment variables in your deployment platform:

### Required Variables

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
VISION_CREDENTIALS_PATH=your_credentials
```

### VISION_CREDENTIALS_PATH Options

You have two options for setting `VISION_CREDENTIALS_PATH`:

#### Option 1: File Path (Local Development)
```bash
VISION_CREDENTIALS_PATH=/path/to/gen-lang-client-0250729981-f4854d1a53eb.json
```

#### Option 2: JSON Content (Cloud Deployment) ⭐ **Recommended**
```bash
VISION_CREDENTIALS_PATH='{"type":"service_account","project_id":"gen-lang-client-0250729981",...}'
```

**For cloud deployment, use Option 2** - paste the entire JSON content of your service account key.

## 🐳 Docker Deployment

### Local Docker Compose

1. Create a `.env` file with your environment variables:
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
VISION_CREDENTIALS_PATH='{"type":"service_account",...}'
```

2. Run the application:
```bash
docker-compose up --build
```

### Cloud Deployment

#### Heroku
1. Set environment variables in Heroku dashboard
2. Deploy using Heroku CLI or GitHub integration
3. The `Procfile` and `runtime.txt` are already configured

#### Railway/Render/Other Platforms
1. Set environment variables in your platform's dashboard
2. Deploy using the Dockerfile
3. Ensure all environment variables are set

## 🔍 Validation

Run the setup script to validate your deployment:

```bash
python setup_deployment.py
```

This will check:
- ✅ All required environment variables are set
- ✅ Credentials file/content is valid
- ✅ Required directories exist

## 🚀 Deployment Checklist

Before deploying, verify:

- [ ] All environment variables are set
- [ ] VISION_CREDENTIALS_PATH contains valid JSON (for cloud deployment)
- [ ] Supabase project is configured with required buckets
- [ ] Google Cloud Vision API is enabled
- [ ] Gemini API key is valid

## 🐛 Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all environment variables are set in your deployment platform

2. **"Credentials file not found"**
   - For cloud deployment, use JSON content instead of file path
   - For local deployment, ensure the file path is correct

3. **Health check failures**
   - The Dockerfile now includes curl for health checks
   - Ensure the application starts properly

4. **Volume mount errors**
   - Directories are created automatically
   - Volumes have read-write permissions

### Testing Locally

```bash
# Test environment setup
python setup_deployment.py

# Test with Docker
docker-compose up --build

# Test health check
curl http://localhost:8000/
```

## 📞 Support

If you encounter issues:

1. Check the application logs
2. Verify environment variables are set correctly
3. Ensure all API keys are valid and have proper permissions
4. Test the setup script: `python setup_deployment.py` 