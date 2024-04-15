import dotenv
import os

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "appointment")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = int(os.getenv("PORT", "8000"))

if OPENAI_API_KEY is None:
    raise BaseException("need to setup OPENAI_API_KEY environment variable")