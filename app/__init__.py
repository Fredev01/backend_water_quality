from fastapi import FastAPI
from app.features.auth import auth_router
from app.share.firebase import initialize
from app.share.firebase.domain.config import FirebaseConfigImpl

app = FastAPI()

firebase_admin = initialize(FirebaseConfigImpl())


app.include_router(auth_router)


@app.get("/")
def get_index():
    return {"message": "API"}
