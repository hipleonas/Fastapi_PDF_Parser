import os
import shutil
import tempfile
from typing import Dict

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VALID_TOKEN = os.getenv("BEARER_TOKEN", "test")  # Default to "test" for development
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Security
security = HTTPBearer()

# FastAPI app configuration
app = FastAPI(
    title="PDF Parser API",
    description="A FastAPI application for parsing PDF documents using Docling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify the bearer token for authentication

    Args:
        credentials: HTTP authorization credentials

    Returns:
        str: The verified token

    Raises:
        HTTPException: If token is invalid or missing
    """
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# API Routes
@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information

    Returns:
        Dict containing API information
    """
    return {
        "message": "PDF Parser API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint

    Returns:
        Dict containing health status
    """
    return {"status": "healthy", "service": "pdf-parser-api"}


@app.post(
    "/upload-pdf/",
    tags=["PDF Processing"],
    summary="Parse PDF document",
    description="Upload a PDF file and get parsed content in structured format",
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    token: str = Depends(verify_token),
):
    """
    Parse PDF document and return structured content

    Args:
        file: PDF file to be processed
        token: Authentication token (verified by dependency)

    Returns:
        dict: Structured PDF content with paragraphs

    Raises:
        HTTPException: For various error conditions
    """
    # Create temporary file
    temp_file = None
    try:
        # Create temporary file with proper suffix
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            # Copy uploaded file content to temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        # Get file size
        file_size = os.path.getsize(temp_path)

        # Initialize document converter
        converter = DocumentConverter()

        # Convert PDF to document
        result = converter.convert(temp_path)
        doc = result.document

        # Export to markdown
        markdown_content = doc.export_to_markdown()

        # Process content into paragraphs
        paragraphs = [
            line.strip()
            for line in markdown_content.split("\n")
            if line.strip() and not line.strip().startswith("#")  # Filter out headers
        ]

        # Create structured response
        structured_paragraphs = [
            {"id": i + 1, "text": para} for i, para in enumerate(paragraphs)
        ]

        return {
            "title": file.filename or "unknown.pdf",
            "paragraphs": structured_paragraphs,
            "total_paragraphs": len(structured_paragraphs),
            "file_size_bytes": file_size,
        }

    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error processing PDF: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF document: {str(e)}",
        )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                print(f"Warning: Could not delete temporary file {temp_path}: {e}")


# Development server configuration
if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
    )

"""
🚀 HOW TO RUN THE APPLICATION:

1. Activate your virtual environment:
   source venv/bin/activate  # On Linux/Mac
   # OR
   venv\Scripts\activate     # On Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Set up environment variables (optional):
   Create a .env file with:
   BEARER_TOKEN=your_secret_token_here

4. Run the application:
   
   For development (with auto-reload):
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   OR simply run:
   python main.py
   
   For production:
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

5. Access the application:
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health
   - API endpoint: http://localhost:8000/upload-pdf/

6. Test the API:
   Use the provided test_curl.sh script:
   chmod +x test_curl.sh
   ./test_curl.sh

📚 Example API Usage:
curl -X POST "http://localhost:8000/upload-pdf/" \
     -H "Authorization: Bearer test" \
     -F "file=@your_document.pdf"
"""
