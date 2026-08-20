import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi import APIRouter
from pydantic import BaseModel

import logging
import database
import gemini

logger = logging.getLogger("api_project")
logging.basicConfig(level=logging.INFO,)
logging.basicConfig(level=logging.ERROR,)

INTERNAL_API_KEY = os.getenv("internal_api_key")

router = APIRouter()

# structure oh question
class Question(BaseModel):
    question:str

# display message error if api key problem
def verify_api_key(x_api_key:str = Header(...)):
    if not INTERNAL_API_KEY:
        raise HTTPException(status_code=500, detail="internal key not configured")
    if x_api_key !=INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="invalide API key")

    # end points
@router.get("/")
def root():
    return{"message":"online"}

@router.get("/health/database")
def health_database(_: None = Depends(verify_api_key)):
    try:
        rows = database.get_general_catalog_sample(limit=5)
        return {"database_conected": True, "acces to database": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"connexion error to database:{e}")

@router.post("/ask")
def ask(payload: Question, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)

    question = payload.question.strip()
    if not question:
        logger.exception("question error")
        raise HTTPException(status_code=400, detail="no question")

    try:
        matches = database.search_products(question)
        if not matches:
            matches = database.get_general_catalog_sample()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"database error: {e}")

    try:
        answer = gemini.ask_gemini(question, matches)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nik ai error: {e}")

    return {
        "question": question,
        "answer": answer,
        "products_used": [m["name"] for m in matches],
    }