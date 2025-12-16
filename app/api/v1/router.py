from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, candidates, notes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(notes.router, prefix="/candidates", tags=["Notes"])
