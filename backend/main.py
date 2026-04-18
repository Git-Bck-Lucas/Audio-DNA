from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.spotify import router as spotify_router
from backend.api.v1.analysis import router as analysis_router
from backend.logging_config import logger

app = FastAPI(
    title='Audio DNA API',
    description='Spotify-based HR Analytics',
    version='0.1.0'
)
logger.info('FastAPI App started')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug('CORS middleware configured')

app.include_router(spotify_router, prefix="/api/v1")
#logger.info('Spotify router registered')
app.include_router(analysis_router, prefix='/api/v1')
#logger.info('Analysis Router registered')

@app.get("/")
async def root():
    return {
        "message": "Welcome to Audio DNA API",
        "status": "running",
        "version": "0.1.0"
    }
    
@app.get("/health")
async def health_check():
    return {"status": "healthy"}