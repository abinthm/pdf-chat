import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
from pdf2img import convert_pdf_to_images
from visionOcr import ImageTextExtractor
from sentence_transformers import SentenceTransformer
import requests
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from storage3.exceptions import StorageApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VISION_CREDENTIALS_PATH = os.getenv("VISION_CREDENTIALS_PATH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate all required environment variables
missing_vars = []
if not SUPABASE_URL:
    missing_vars.append("SUPABASE_URL")
if not SUPABASE_KEY:
    missing_vars.append("SUPABASE_KEY")
if not GEMINI_API_KEY:
    missing_vars.append("GEMINI_API_KEY")

# VISION_CREDENTIALS_PATH is optional for cloud deployment
if not VISION_CREDENTIALS_PATH:
    print("⚠️  VISION_CREDENTIALS_PATH not set - will use default service account (cloud deployment)")

if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Handle VISION_CREDENTIALS_PATH - support both file path and JSON content
def setup_vision_credentials(credentials_path_or_json=None):
    """Setup Google Cloud Vision credentials from file path or JSON content"""
    import tempfile
    import json
    
    # If no credentials provided, use default service account (cloud deployment)
    if not credentials_path_or_json:
        print("Using default service account for Vision API")
        return None
    
    # Check if it's a valid JSON string (credentials content)
    try:
        json.loads(credentials_path_or_json)
        # It's JSON content, create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(credentials_path_or_json)
        temp_file.close()
        return temp_file.name
    except (json.JSONDecodeError, TypeError):
        # It's a file path, check if file exists
        if os.path.exists(credentials_path_or_json):
            return credentials_path_or_json
        else:
            raise FileNotFoundError(f"Credentials file not found: {credentials_path_or_json}")

# Setup vision credentials (can be None for cloud deployment)
VISION_CREDENTIALS_FILE = setup_vision_credentials(VISION_CREDENTIALS_PATH)

# Create Supabase client with basic configuration
# Note: We'll handle timeouts at the request level since Supabase client doesn't support custom HTTP client easily
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="PDF Chatbot Backend", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "PDF Chatbot Backend API",
        "version": "1.0.0",
        "endpoints": {
            "upload_pdf": "/upload_pdf/",
            "ask_question": "/ask/"
        }
    }

def extract_text_from_pdf_images(pdf_id: str) -> list:
    """
    Extract text from images in the 'pdfimg' bucket for a given pdf_id, upload text files to 'pdftxt' bucket.
    Returns a list of uploaded text file paths.
    """
    import time
    img_bucket = "pdfimg"
    txt_bucket = "pdftxt"
    img_folder = f"{pdf_id}"
    # Wait for storage to sync
    time.sleep(2)
    # List images in the bucket
    files = supabase.storage.from_(img_bucket).list(img_folder)
    print("Raw list response:", files)
    if hasattr(files, 'data'):
        files = files.data
    print(f"Files in bucket after upload for {pdf_id}:", files)
    if not files:
        logger.warning(f"No images found in bucket '{img_bucket}' for pdf_id '{pdf_id}'")
        return []
    # Prepare local temp dir
    local_img_dir = f"temp_images/{pdf_id}"
    os.makedirs(local_img_dir, exist_ok=True)
    local_image_paths = []
    for img in files:
        img_name = img['name']
        img_storage_path = f"{pdf_id}/{img_name}"
        img_local_path = os.path.join(local_img_dir, img_name)
        img_bytes = supabase.storage.from_(img_bucket).download(img_storage_path)
        with open(img_local_path, "wb") as f:
            f.write(img_bytes)
        local_image_paths.append(img_local_path)
    # Extract text using visionOcr.py
    extractor = ImageTextExtractor(VISION_CREDENTIALS_FILE)
    uploaded_texts = []
    for img_path in local_image_paths:
        text = extractor.extract_text_from_image(img_path)
        txt_name = os.path.splitext(os.path.basename(img_path))[0] + "_text.txt"
        txt_local_path = os.path.join(local_img_dir, txt_name)
        with open(txt_local_path, "w", encoding="utf-8") as f:
            f.write(text)
        # Upload to pdftxt bucket
        txt_storage_path = f"{pdf_id}/{txt_name}"
        with open(txt_local_path, "rb") as f_txt:
            upload_res = supabase.storage.from_(txt_bucket).upload(txt_storage_path, f_txt, file_options={"content-type": "text/plain"})
            if getattr(upload_res, "error", None):
                logger.error(f"Failed to upload text file {txt_name}: {upload_res.error['message']}")
            else:
                uploaded_texts.append(txt_storage_path)
    # Clean up local temp files
    shutil.rmtree(local_img_dir)
    return uploaded_texts

model = SentenceTransformer('all-MiniLM-L6-v2')

genai.configure(api_key=GEMINI_API_KEY)



def ask_gemini(question, context, gemini_model="models/gemini-2.5-flash"):
    import google.api_core.exceptions
    prompt = (
        "You are a helpful assistant. Use the following context from a PDF to answer the user's question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    try:
        model = genai.GenerativeModel(gemini_model)
        response = model.generate_content(prompt)
        return response.text.strip()
    except google.api_core.exceptions.ResourceExhausted as e:
        # Quota error, try fallback model
        if gemini_model != "models/gemini-2.5-flash-lite":
            try:
                model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
                response = model.generate_content(prompt)
                return response.text.strip() + "\n\n(Note: Fallback to Flash-Lite due to quota limits.)"
            except Exception as e2:
                return f"Sorry, the AI service is currently rate-limited. Please try again later. (Both Flash and Flash-Lite quota exceeded.)"
        else:
            return f"Sorry, the AI service is currently rate-limited. Please try again later. (Flash-Lite quota exceeded.)"
    except Exception as e:
        return f"Sorry, an error occurred with the AI service: {e}"

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save the uploaded file to a temporary location
    temp_filename = f"temp_{uuid.uuid4()}.pdf"
    with open(temp_filename, "wb") as f:
        content = await file.read()
        f.write(content)

    # Insert PDF metadata into Supabase (without storage_path for now)
    try:
        pdf_name = file.filename
        upload_date = datetime.utcnow().isoformat()
        data = supabase.table("pdfs").insert({"name": pdf_name, "upload_date": upload_date}).execute()
        pdf_id = data.data[0]["id"]
    except Exception as e:
        print("Exception occurred:", e)
        os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Upload the PDF to Supabase Storage
    bucket_name = "pdfs"
    storage_path = f"{pdf_id}/{file.filename}"
    
    # Check file size before upload (Supabase free tier limit is 50MB)
    file_size = os.path.getsize(temp_filename)
    file_size_mb = file_size / (1024 * 1024)
    supabase_free_tier_limit_mb = 50
    
    if file_size_mb > supabase_free_tier_limit_mb:
        os.remove(temp_filename)
        raise HTTPException(
            status_code=413, 
            detail={
                "error": "File too large for Supabase free tier",
                "file_size_mb": f"{file_size_mb:.1f}MB",
                "supabase_free_tier_limit": f"{supabase_free_tier_limit_mb}MB",
                "message": f"Your file ({file_size_mb:.1f}MB) exceeds the Supabase free tier limit of {supabase_free_tier_limit_mb}MB per file.",
                "solution": "Upgrade to Supabase Pro ($25/month) for 5GB file limits"
            }
        )
    
    try:
        with open(temp_filename, "rb") as f:
            res = supabase.storage.from_(bucket_name).upload(storage_path, f, file_options={"content-type": "application/pdf"})
        if getattr(res, "error", None):
            os.remove(temp_filename)
            raise HTTPException(status_code=500, detail=f"Storage error: {res.error['message']}")
    except StorageApiError as e:
        os.remove(temp_filename)
        if "413" in str(e) or "payload too large" in str(e).lower() or "exceeded the maximum allowed size" in str(e).lower():
            raise HTTPException(
                status_code=413, 
                detail={
                    "error": "File too large for Supabase storage",
                    "file_size_mb": f"{file_size_mb:.1f}MB",
                    "supabase_free_tier_limit": f"{supabase_free_tier_limit_mb}MB",
                    "message": f"Your file ({file_size_mb:.1f}MB) exceeds the Supabase free tier limit of {supabase_free_tier_limit_mb}MB per file.",
                    "solution": "Upgrade to Supabase Pro ($25/month) for 5GB file limits"
                }
            )
        else:
            raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        os.remove(temp_filename)
        logger.error(f"PDF upload failed for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF upload failed: {str(e)}")

    # Update the pdfs table with the storage path
    try:
        supabase.table("pdfs").update({"storage_path": storage_path}).eq("id", pdf_id).execute()
    except Exception as e:
        os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=f"Failed to update storage path: {str(e)}")

    # Clean up temp file
    os.remove(temp_filename)

    # --- Download PDF from bucket, convert to images locally ---
    downloaded_pdf_path = f"{pdf_id}_{file.filename}"
    
    # Verify the PDF was uploaded successfully before proceeding
    try:
        download_res = supabase.storage.from_(bucket_name).download(storage_path)
        with open(downloaded_pdf_path, "wb") as f:
            f.write(download_res)
        logger.info(f"Successfully downloaded PDF for processing: {file.filename}")
    except Exception as e:
        logger.error(f"Failed to download PDF from storage: {str(e)}")
        # Clean up the database entry since storage upload failed
        try:
            supabase.table("pdfs").delete().eq("id", pdf_id).execute()
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup database entry: {cleanup_error}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "PDF upload verification failed",
                "message": f"PDF was not uploaded successfully to storage. Error: {str(e)}",
                "file": file.filename
            }
        )

    # 1. Convert PDF to images locally
    output_dir = f"images/{pdf_id}"
    os.makedirs(output_dir, exist_ok=True)
    image_paths = convert_pdf_to_images(downloaded_pdf_path, output_dir)

    # 2. Upload images to the 'pdfimg' bucket
    img_bucket = "pdfimg"
    uploaded_images = []
    for img_path in image_paths:
        img_name = os.path.basename(img_path)
        img_storage_path = f"{pdf_id}/{img_name}"
        
        # Retry logic for upload with better error handling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(img_path, "rb") as img_file:
                    logger.info(f"Starting upload for {img_name} (attempt {attempt + 1}/{max_retries})")
                    upload_res = supabase.storage.from_(img_bucket).upload(img_storage_path, img_file, file_options={"content-type": "image/jpeg"})
                    
                    if getattr(upload_res, "error", None):
                        logger.error(f"Failed to upload image {img_name}: {upload_res.error['message']}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying upload for {img_name} (attempt {attempt + 2}/{max_retries})")
                            continue
                    else:
                        uploaded_images.append(img_storage_path)
                        logger.info(f"Successfully uploaded {img_name}")
                        break
                        
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1} failed for {img_name}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying upload for {img_name} (attempt {attempt + 2}/{max_retries})")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to upload {img_name} after {max_retries} attempts")

    # 3. Extract text from local images and upload to 'pdftxt' bucket
    extractor = ImageTextExtractor(VISION_CREDENTIALS_FILE)
    uploaded_texts = []
    for img_path in image_paths:
        text = extractor.extract_text_from_image(img_path)
        txt_name = os.path.splitext(os.path.basename(img_path))[0] + "_text.txt"
        txt_local_path = os.path.join(output_dir, txt_name)
        with open(txt_local_path, "w", encoding="utf-8") as f:
            f.write(text)
        txt_storage_path = f"{pdf_id}/{txt_name}"
        
        # Retry logic for text file upload
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(txt_local_path, "rb") as f_txt:
                    logger.info(f"Starting text upload for {txt_name} (attempt {attempt + 1}/{max_retries})")
                    upload_res = supabase.storage.from_("pdftxt").upload(txt_storage_path, f_txt, file_options={"content-type": "text/plain"})
                    if getattr(upload_res, "error", None):
                        logger.error(f"Failed to upload text file {txt_name}: {upload_res.error['message']}")
                        if attempt < max_retries - 1:
                            logger.info(f"Retrying text upload for {txt_name} (attempt {attempt + 2}/{max_retries})")
                            continue
                    else:
                        uploaded_texts.append(txt_storage_path)
                        logger.info(f"Successfully uploaded text file {txt_name}")
                        break
            except Exception as e:
                logger.error(f"Text upload attempt {attempt + 1} failed for {txt_name}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying text upload for {txt_name} (attempt {attempt + 2}/{max_retries})")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to upload text file {txt_name} after {max_retries} attempts")
        # --- Generate and store embedding ---
        # Extract page number from txt_name (expects format 'page_XXX_text.txt')
        try:
            page_number = int(txt_name.split('_')[1])
        except Exception:
            page_number = None
        embedding = model.encode(text).tolist()
        # Insert into Supabase embeddings table
        try:
            supabase.table("embeddings").insert({
                "pdf_id": pdf_id,
                "page_number": page_number,
                "text": text,
                "embedding": embedding
            }).execute()
        except Exception as e:
            logger.error(f"Failed to insert embedding for {txt_name}: {e}")

    # 4. Clean up local files
    import shutil
    shutil.rmtree(output_dir)
    os.remove(downloaded_pdf_path)

    return JSONResponse({
        "message": "PDF uploaded, images extracted and uploaded, text extracted and uploaded.",
        "pdf_id": pdf_id,
        "pdf_name": pdf_name,
        "upload_date": upload_date,
        "storage_path": storage_path,
        "uploaded_images": uploaded_images,
        "uploaded_texts": uploaded_texts
    })

@app.post("/ask/")
async def ask_question(
    question: str = Body(...),
    pdf_id: str = Body(...),
    match_count: int = Body(3),
    gemini_model: str = Body("models/gemini-2.5-flash")
):
    # 1. Generate embedding for the question
    question_embedding = model.encode(question).tolist()
    # 2. Call Supabase REST API to run match_embeddings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    url = f"{SUPABASE_URL}/rest/v1/rpc/match_embeddings"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "query_embedding": question_embedding,
        "match_pdf_id": pdf_id,
        "match_count": match_count
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)  # 60 second timeout
    resp.raise_for_status()
    results = resp.json()
    # 3. Return the best match(es)
    answers = []
    for r in results:
        answers.append({
            "answer": r["text"],
            "page_number": r["page_number"],
            "pdf_id": r["pdf_id"],
            "similarity": r["similarity"]
        })
    # 4. RAG: Use Gemini to generate a final answer
    context = "\n\n".join([a["answer"] for a in answers])
    rag_answer = ask_gemini(question, context, gemini_model=gemini_model)
    return {
        "rag_answer": rag_answer,
        "matches": answers
    } 