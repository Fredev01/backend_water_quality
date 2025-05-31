from fastapi import FastAPI
from app.features.auth import auth_router
from app.features.workspaces import workspaces_router
from app.features.meters import meters_router
from app.features.alerts import alerts_router
from app.features.users import users_router
from app.share.firebase import FirebaseInitializer
from app.share.firebase.domain.config import FirebaseConfigImpl
from app.share.socketio import socket_app

app = FastAPI()

app.mount("/socket.io/", socket_app, name="socketio")


FirebaseInitializer.initialize(FirebaseConfigImpl())

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(meters_router)
app.include_router(alerts_router)
app.include_router(users_router)


@app.get("/")
def get_index():
    return {"message": "API"}
