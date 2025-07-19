from fastapi import status,HTTPException,Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
load_dotenv()
security = HTTPBearer()
VALID_TOKEN = os.getenv("BEARER_TOKEN")

if not VALID_TOKEN:
    raise ValueError("BEARER_TOKEN is missing from environment!")
def token_verification(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
