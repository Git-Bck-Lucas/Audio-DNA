from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware # Filter between the requests
from backend.api.v1.spotify import router as spotify_router
from backend.api.v1.analysis import router as analysis_router

# Create FastAPI APP
app = FastAPI(
    title='Audio DNA API',
    description='Spotify-based HR Analytics',
    version='0.1.0'
)

# Allows requests from other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow requests from all domains, later in production only specific domains
    allow_credentials=True, # Allow Cookies and Auth-Header
    allow_methods=["*"], # Allow all HTTP Methods --> GET, POST, PUT, DELETE
    allow_headers=["*"], # Allow all hhtp Headers
)

# include router
app.include_router(spotify_router, prefix="/api/v1")
app.include_router(analysis_router, prefix='/api/v1')


# Define Endpoints
@app.get("/") #  Diese Funktion wird aufgerufen, wenn jemand GET macht
async def root(): # asnync def wartet auf andere Dinge
    return {
        "message": "Welcome to Audio DNA API",
        "status": "running",
        "version": "0.1.0"
    }
    
@app.get("/health") # http://127.0.0.1:8000/health
async def health_check():
    return {"status": "healthy"}