from fastapi import FastAPI, HTTPException, Depends,status,UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import shutil
import fitz
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
load_dotenv()
security = HTTPBearer()
VALID_TOKEN = os.getenv("BEARER_TOKEN")
app = FastAPI()

def token_verification(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return credentials.credentials

def extract_text_from_pdf(pdf_path: str) -> str:

    doc = fitz.open(pdf_path)

    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    token: None = Depends(token_verification)

):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    converter = DocumentConverter()
    text = converter.convert(temp_path, "text")
    os.remove(temp_path)

    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    docling_json = {
        "title": file.filename,
        "paragraphs": [{"id": i + 1, "text": para} for i,para in enumerate(paragraphs)],
    }
    return docling_json 


"""
Tested PDF data

https://arxiv.org/pdf/2010.04408
https://arxiv.org/pdf/1512.03385


"""
source = "paper.pdf"



