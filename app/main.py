# app/main.py

from fastapi import FastAPI
from app.api.websocket_routes import router as websocket_router
from app.api.interview_routes import router as interview_router

app = FastAPI()

app.include_router(interview_router)
app.include_router(websocket_router)

@app.on_event("startup")
def debug_routes():
    for route in app.routes:
        print(route.path)
