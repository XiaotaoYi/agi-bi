from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from controller.process_query_api import router as process_query_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="visualization/templates")
app.mount("/static", StaticFiles(directory="visualization/static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

# Import and include the process_query router
app.include_router(process_query_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True) 