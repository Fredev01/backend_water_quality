from fastapi import FastAPI
from app.features.auth import auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
def get_index():
    return {"message": "API"}
