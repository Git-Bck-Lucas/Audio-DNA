from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/callback"
    ANTHROPIC_API_KEY: str
    
    class Config:
        env_file = ".env"
        
settings = Settings()
    