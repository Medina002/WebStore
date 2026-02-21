import os

class Config:
    # Database credentials
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
    DB_NAME = os.getenv("DB_NAME", "webshop")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Ensure the config is used if running directly (optional)
if __name__ == "__main__":
    cfg = Config()
    print("Database URI:", cfg.SQLALCHEMY_DATABASE_URI)