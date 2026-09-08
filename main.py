import os
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

from api import (
    person1_api,
    clustering_api,
    prediction_api,
    visualization_api,
    intelligence_api,
    dashboard_api,
    insight_api,
    chat_api,
    supabase_api
)

load_dotenv()

app = FastAPI(
    title="Automated Insight Analyst API",
    description="Backend AI/ML analytical services for dataset understanding, cleaning, clustering, forecasting, visualization, intelligence, and summary generation.",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "status_code": 422,
            "detail": exc.errors()
        }
    )

# Include Router Modules
app.include_router(person1_api.router)
app.include_router(clustering_api.router)
app.include_router(prediction_api.router)
app.include_router(visualization_api.router)
app.include_router(intelligence_api.router)
app.include_router(dashboard_api.router)
app.include_router(insight_api.router)
app.include_router(chat_api.router)
app.include_router(supabase_api.router)

# React Frontend Mount
react_dist_dir = os.path.join(os.path.dirname(__file__), "insight-analyst-app", "dist")
react_assets_dir = os.path.join(react_dist_dir, "assets")
if os.path.exists(react_assets_dir):
    app.mount("/assets", StaticFiles(directory=react_assets_dir), name="react_assets")

# Mount Static Files for Developer Testing Interface
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/clarion-data-logo.png")
def get_clarion_logo():
    logo_dist = os.path.join(react_dist_dir, "clarion-data-logo.png")
    if os.path.exists(logo_dist):
        return FileResponse(logo_dist, media_type="image/png")
    logo_public = os.path.join(os.path.dirname(__file__), "insight-analyst-app", "public", "clarion-data-logo.png")
    if os.path.exists(logo_public):
        return FileResponse(logo_public, media_type="image/png")
    raise HTTPException(status_code=404, detail="Clarion Data Logo not found")

@app.get("/")
def read_root():
    react_index = os.path.join(react_dist_dir, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "service": "Automated Insight Analyst API",
        "documentation": "/docs"
    }

@app.get("/test-ui")
def read_test_ui():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Test UI not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
