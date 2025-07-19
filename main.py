from fastapi import FastAPI, HTTPException, Depends,status,UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import shutil
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

@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    token: str = Depends(token_verification)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        converter = DocumentConverter()
        doc = converter.convert(temp_path).document
        markdown_content = doc.export_to_markdown()
        paragraphs = [p.strip() for p in markdown_content.split('\n') if p.strip()]
        docling_json = {
            "title": file.filename,
            "paragraphs": [{"id": i + 1, "text": para} for i, para in enumerate(paragraphs)],
        }

        return docling_json
    finally:
        # Xóa file tạm để tránh lưu rác
        if os.path.exists(temp_path):
            os.remove(temp_path)


"""
Tested PDF data

https://arxiv.org/pdf/2010.04408
https://arxiv.org/pdf/1512.03385


"""




