import os
from dotenv import load_dotenv

load_dotenv()

NEXUS_API_KEY = os.getenv("NEXUS_API_KEY", "")
NEXUS_BASE_URL = os.getenv("NEXUS_BASE_URL", "")
NEXUS_MODEL = os.getenv("NEXUS_MODEL", "gpt-4o-mini")

# Multilingual embedding model (supports Tamil + English), runs locally
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TOP_K = 4
