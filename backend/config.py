import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://localhost/planeaai")
    FIREBASE_SERVICE_ACCOUNT: dict = json.loads(
        os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "{}")
    )
    STRIPE_SECRET_KEY: str = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_PRO: str = os.environ.get("STRIPE_PRICE_PRO", "")
    STRIPE_PRICE_ESCUELA: str = os.environ.get("STRIPE_PRICE_ESCUELA", "")
    GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "production")
    TESTING: bool = False


class TestConfig(Config):
    DATABASE_URL: str = "sqlite:///:memory:"
    TESTING: bool = True
    FIREBASE_SERVICE_ACCOUNT: dict = {}
