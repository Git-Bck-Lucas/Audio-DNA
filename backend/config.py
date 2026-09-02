from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/callback"
    ANTHROPIC_API_KEY: str
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SESSION_SECRET_KEY: str
    TOKEN_ENCRYPTION_KEY: str
    FRONTEND_URL: str = "http://localhost:5173"
    COOKIE_SECURE: bool = False
    
    class Config:
        env_file = ".env"
        
settings = Settings()
    