import requests
import re
import random
import html
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from app.config import USERNAME, PASSWORD



def calcular_periodo():

    agora = datetime.now() - timedelta(minutes=5)
    uma_hora = agora - timedelta(hours=1)

    return {
        "dataI": uma_hora.strftime("%d/%m/%Y"),
        "dataF": agora.strftime("%d/%m/%Y"),
        "horaI": uma_hora.strftime("%H:%M"),
        "horaF": agora.strftime("%H:%M"),
    }


def login(session, base_url):

    login_url = f"{base_url}/security/validate"

    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
        "Origin": base_url,
        "Referer": f"{base_url}/security/login"
    }

    r = session.post(login_url, data=payload, headers=headers, timeout=15)

    if r.status_code != 200:
        raise Exception(f"Erro no login {base_url}")

    print(f"Login realizado: {base_url}")


def abrir_relatorio(session, base_url):

    view_url = f"{base_url}/relatorioEstatisticaSIP/view"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{base_url}/dashboard"
    }

    r = session.get(view_url, headers=headers, timeout=15)

    if r.status_code != 200:
        raise Exception(f"Erro ao abrir relatório {base_url}")

    print(f"Relatório carregado: {base_url}")


def pegar_rotas(session, base_url):

    view_url = f"{base_url}/relatorioEstatisticaSIP/view"

    r = session.get(view_url, timeout=15)

    html_page = r.text

    rotas = re.findall(
        r'<option value="(\d+)".*?>(.*?)</option>',
        html_page
    )

    rotas_validas = [
        {"id": r[0], "nome": r[1].strip()}
        for r in rotas
        if r[0] not in ("0", "")
    ]

    print(f"{base_url} → Rotas encontradas: {len(rotas_validas)}")

    return rotas_validas


def consultar_rota(session, base_url, rota, periodo):

    try:

        data_url = f"{base_url}/relatorioEstatisticaSIP/data"
        view_url = f"{base_url}/relatorioEstatisticaSIP/view"

        params = {
            str(random.random()): "",
            "relatorioAlarmes": "DESC",
            "SORT_CHANGE": "",
            "SORT_TAG": "create_date",
            "PAGE": "1",
            "txtDataI": periodo["dataI"],
            "txtDataF": periodo["dataF"],
            "txtHoraInicial": periodo["horaI"],
            "txtHoraFinal": periodo["horaF"],
            "txtRota": rota["id"]
        }

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": view_url,
            "User-Agent": "Mozilla/5.0"
        }

        r = session.get(
            data_url,
            params=params,
            headers=headers,
            timeout=20
        )

        if "Nenhum registro" in r.text:
            return []

        matches = re.findall(
            r"name:\s*'([^']+)'\s*,\s*y:\s*(\d+)",
            r.text
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dados = []

        for nome, valor in matches:

            quantidade = int(valor)

            if quantidade == 0:
                continue

            dados.append({
                "timestamp": timestamp,
                "rota": rota["nome"],
                "sip_code": html.unescape(nome),
                "quantidade": quantidade
            })

        return dados

    except Exception as e:

        print(f"Erro rota {rota['nome']} → {e}")
        return []


def coletar_sip_stats(base_url):

    session = requests.Session()

    login(session, base_url)
    abrir_relatorio(session, base_url)

    periodo = calcular_periodo()
    rotas = pegar_rotas(session, base_url)

    resultados = []
    periodo = calcular_periodo()

    print(
        f"Período: {periodo['dataI']} {periodo['horaI']} "
        f"→ {periodo['dataF']} {periodo['horaF']}"
    )
    print(f"Iniciando coleta sequencial: {base_url}")

    for rota in rotas:
        dados = consultar_rota(session, base_url, rota, periodo)
        resultados.extend(dados)
        time.sleep(0.6)  # intervalo mínimo entre cada rota

    print(f"Coleta finalizada: {base_url} → {len(resultados)} registros")

    return resultados