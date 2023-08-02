from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres", "postgresql")


class EmailConfig:
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
