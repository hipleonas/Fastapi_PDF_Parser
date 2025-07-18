from fastapi import FastAPI,File, HTTPException, UploadFile, Depends,status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

import docling
import os
"""

Documentation on FastAPI can be found at : 

Some important notes
HTTPBearer: http là một loại mã thông báo sử dụng để xác thực ủy quyền
và được sử dụng trong các ứng dựng web và API 
=> Mục đích lưu trữ thông tin xác thực của người dùng và chỉ định ủy quyền
cho các yêu cầu quyền truy cập
Ví dụ : Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva
Sự khác biệt giữa Bearer và API keys
+ Included in the Authorization header using "Bearer" scheme
+ Versatile, supports fine-grained access control, OAuth 2.0 usage
+ Generally considered more secure, supports token expiration

"""

app = FastAPI()
security = HTTPBearer()

VALID_TOKEN = os.getenv("API_TOKEN", "secret_token")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != VALID_TOKEN or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token might be expired or invalid",
        )
    return credentials.credentials

@app.pos("/parse-pdf" )
async def parse_pdf(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)

):
    #Check the format of the file 
    if not  file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "File must be a PDF",
        )
    try:
        #This part we use docling
        file_content = await file.read()
        text_parsing = docling.parse_pdf(file_content)

        if text_parsing is None:
            from PyPDF2 import PdfReader
            import io
            reader = PdfReader(io.BytesIO(file_content))
            parsed_text = "\n".join([page.extract_text() for page in reader.pages])
        return {"filename": file.filename, "text": parsed_text}
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"An error occured while processing the PDF: {str(e)}"
        )
@app.get("/")

def read_root():
    return {"message" : "PDF Parser API is currenly running. Please use the /parse-pdf endpoint to parse your PDF files."}
        