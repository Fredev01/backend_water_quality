from fastapi import FastAPI
from app.features.auth import auth_router
from app.features.workspaces import workspaces_router
from app.share.firebase import FirebaseInitializer
from app.share.firebase.domain.config import FirebaseConfigImpl

app = FastAPI()


FirebaseInitializer.initialize(FirebaseConfigImpl())

app.include_router(auth_router)
app.include_router(workspaces_router)


@app.get("/")
def get_index():
    return {"message": "API"}
