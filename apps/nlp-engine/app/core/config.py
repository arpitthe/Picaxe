import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv(
        "PROJECT_NAME",
        "Picaxe NLP Engine",
    )

    PORT: int = int(
        os.getenv("PORT", "8001")
    )

    HOST: str = os.getenv(
        "HOST",
        "0.0.0.0",
    )


settings = Settings()