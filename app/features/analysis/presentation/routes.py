from fastapi import APIRouter, Depends
from app.share.jwt.infrastructure import verify_access_token

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])


@analysis_router.get("/")
def get_analysis(
    user=Depends(verify_access_token),
):
    return {"message": "Analysis endpoint"}


@analysis_router.post("/avarage/")
def create_avarage(
    user=Depends(verify_access_token),
):
    return {"message": "Create avarage analysis"}
