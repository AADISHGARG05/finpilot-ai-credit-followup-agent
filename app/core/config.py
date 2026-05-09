from dotenv import load_dotenv
import os
load_dotenv()
GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)
MODEL_NAME = (
    "llama-3.3-70b-versatile"
)
DATABASE_NAME = "audit.db"
DRY_RUN_MODE = True