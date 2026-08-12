import os

class Settings:
    PROJECT_NAME: str = "Picaxe NLP Engine"
    PORT: int = int(os.getenv("PORT", 8001))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()
