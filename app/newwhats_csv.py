import csv
import os
import re
from bs4 import BeautifulSoup

BASE_URL = "https://newwhats.nvtelecom.com.br"


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def baixar_csv_historico(session, first_day, last_day, filename="historico.csv"):

    # criar pasta output se não existir
    os.makedirs("output", exist_ok=True)

    # pegar token
    r = session.get(f"{BASE_URL}/historico", timeout=30)

    if r.status_code != 200:
        raise Exception("Erro acessando página de histórico")

    soup = BeautifulSoup(r.text, "html.parser")

    token_input = soup.find("input", {"name": "_token"})

    if not token_input:
        raise Exception("Token CSRF não encontrado")

    token = token_input["value"]

    payload = {
        "_token": token,
        "_method": "post",
        "id_usuario": "0",
        "first_day": first_day,
        "last_day": last_day,
        "tarifa": "",
        "tarifa_v2": "",
        "v2": "3",
        "length": "10000",
        "start": "0"
    }

    r = session.post(
        f"{BASE_URL}/historico",
        data=payload,
        timeout=60
    )

    if "login" in r.url.lower():
        raise Exception("Sessão expirou no NewWhats")

    soup = BeautifulSoup(r.text, "html.parser")

    linhas = soup.select("#table_id tbody tr")

    dados = []

    for linha in linhas:

        colunas = [limpar(c.get_text()) for c in linha.find_all("td")]

        if len(colunas) < 11:
            continue

        dados.append(colunas)

    headers = [
        "id_campanha",
        "tipo",
        "nome",
        "centro_custo",
        "cliente",
        "registro",
        "arquivo",
        "envios",
        "blacklist",
        "erros",
        "valor",
        "status"
    ]

    file_path = os.path.join("output", filename)

    with open(file_path, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(headers)

        writer.writerows(dados)

    return file_path