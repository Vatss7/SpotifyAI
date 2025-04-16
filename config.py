import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
logger.info("Loaded API credentials from environment variables (.env)")
