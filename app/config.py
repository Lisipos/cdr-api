import os

API_BASE_URL = os.getenv("API_BASE_URL")

API_TOKEN = os.getenv("EXTERNAL_API_TOKEN")
API_KEY = os.getenv("EXTERNAL_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
EMAIL_WHATS = os.getenv("EMAIL_WHATS")
PASSWORD_WHATS = os.getenv("PASSWORD_WHATS")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID")
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")

EMAIL_FROM = "felipe.uglar@nvtelecom.com.br"
EMAIL_TO = [
    "felipe.uglar@nvtelecom.com.br",
    "gabriel.veloso@nvtelecom.com.br"
]

LIMITE_COMPLETAMENTO = 5

SERVIDORES = {
    "SP1": "https://newvoz.nvtelecom.com.br",
    "SP1_NOVA": "https://sp1-newvoz.nvtelecom.com.br",
    "SP2": "https://sp2-newvoz.nvtelecom.com.br"
}


def get_api_url():
    return f"{API_BASE_URL}/{API_TOKEN}/{API_KEY}"
