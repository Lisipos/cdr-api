import requests
from bs4 import BeautifulSoup

BASE_URL = "https://newwhats.nvtelecom.com.br"


def login_newwhats(email, password):

    session = requests.Session()

    # headers padrão de navegador
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    })

    # -----------------------------
    # 1 - abrir página de login
    # -----------------------------
    r = session.get(f"{BASE_URL}/login", timeout=30)

    if r.status_code != 200:
        raise Exception("Não foi possível acessar a página de login")

    soup = BeautifulSoup(r.text, "html.parser")

    token_input = soup.find("input", {"name": "_token"})

    if not token_input:
        raise Exception("Token CSRF não encontrado na página de login")

    token = token_input["value"]

    # -----------------------------
    # 2 - payload de login
    # -----------------------------
    payload = {
        "_token": token,
        "email": email,
        "password": password
    }

    headers_post = {
        "Referer": f"{BASE_URL}/login",
        "Origin": BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    login = session.post(
        f"{BASE_URL}/session",
        data=payload,
        headers=headers_post,
        allow_redirects=False,
        timeout=30
    )

    # -----------------------------
    # validar resposta
    # -----------------------------
    if login.status_code not in (302, 303):
        raise Exception(f"Falha no login. Status: {login.status_code}")

    location = login.headers.get("Location", "")

    if "/dashboard" not in location:
        raise Exception("Login falhou: redirecionamento inesperado")

    # -----------------------------
    # testar sessão autenticada
    # -----------------------------
    teste = session.get(f"{BASE_URL}/dashboard", timeout=30)

    if "login" in teste.url.lower():
        raise Exception("Sessão inválida após login")

    return session