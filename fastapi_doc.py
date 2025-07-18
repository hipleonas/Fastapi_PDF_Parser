from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}





