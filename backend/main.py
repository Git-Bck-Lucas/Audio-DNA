from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from backend.api.v1.spotify import router as spotify_router
from backend.api.v1.analysis import router as analysis_router
from backend.logging_config import logger
from backend.config import settings

app = FastAPI(
    title='Audio DNA API',
    description='Spotify-based HR Analytics',
    version='0.1.0'
)
logger.info('FastAPI App started')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug('CORS middleware configured')

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    https_only=settings.COOKIE_SECURE,
    same_site='lax',
    # 1 Tag statt 7. Die Session ist das einzige, was die Identitaet des Nutzers
    # traegt -- je laenger sie lebt, desto laenger ueberlebt auch ein falsch
    # zugeordnetes Cookie einen bereits ausgelieferten Fix. Genau das ist passiert:
    # eine Session aus der Zeit vor dem Token-Cache-Fix war Tage spaeter noch gueltig
    # und wies eine fremde Person als User 1 aus. Kuerzere Lebensdauer begrenzt das
    # Zeitfenster. Preis: haeufigeres Neu-Einloggen, bei dieser Nutzungsfrequenz ok.
    max_age=60*60*24
)

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