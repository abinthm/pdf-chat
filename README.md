# PDF Preprocessor - AI-Powered PDF Chatbot

A FastAPI-based backend application that processes PDFs using Google Cloud Vision OCR and provides AI-powered chat functionality using Gemini.

## 🚀 Features

- **PDF Upload & Processing**: Convert PDFs to images and extract text using Google Cloud Vision
- **AI Chat**: Ask questions about your PDFs using Google's Gemini AI
- **Vector Search**: Semantic search through PDF content
- **Cloud Ready**: Deploy to Google Cloud Run, Heroku, or any cloud platform

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Vision API credentials
- Supabase project (for storage)
- Gemini API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pdfprepro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=your_gemini_api_key
   VISION_CREDENTIALS_PATH=your_credentials_json_or_path
   ```

## 🚀 Quick Start

### Local Development
```bash
uvicorn main:app --reload
```

### Docker
```bash
docker-compose up --build
```

### Cloud Deployment
```bash
python deploy_to_cloud_run.py
```

## 📚 API Endpoints

- `GET /` - Health check
- `POST /upload_pdf/` - Upload and process PDF
- `POST /ask/` - Ask questions about uploaded PDFs

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_KEY` | Your Supabase API key | ✅ |
| `GEMINI_API_KEY` | Your Gemini API key | ✅ |
| `VISION_CREDENTIALS_PATH` | Google Cloud Vision credentials | ✅ |

## 🐳 Docker

The application includes Docker support for easy deployment:

```bash
# Build and run locally
docker-compose up --build

# Build image
docker build -t pdfprepro .

# Run container
docker run -p 8000:8000 pdfprepro
```

## ☁️ Cloud Deployment

### Google Cloud Run
```bash
python deploy_to_cloud_run.py
```

### Heroku
```bash
git push heroku main
```

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Simple Deployment Guide](SIMPLE_DEPLOYMENT_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check the [deployment guides](DEPLOYMENT.md)
2. Verify your environment variables
3. Check the application logs
