from dotenv import load_dotenv
load_dotenv()

from endpoints import router
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="API Project")

# permision 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["x-api-key"],
)

app.include_router(router)
