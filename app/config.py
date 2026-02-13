import os

API_BASE_URL = os.getenv("API_BASE_URL")

API_TOKEN = os.getenv("EXTERNAL_API_TOKEN")
API_KEY = os.getenv("EXTERNAL_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

def get_api_url():
    return f"{API_BASE_URL}/{API_TOKEN}/{API_KEY}"
