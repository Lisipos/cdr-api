import pandas as pd
import requests
import re
import random
import html
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from app.config import USERNAME, PASSWORD, GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, EMAIL_FROM, EMAIL_TO,LIMITE_COMPLETAMENTO



def obter_token():

    url = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"

    payload = {
        "client_id": GRAPH_CLIENT_ID,
        "client_secret": GRAPH_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }

    try:

        r = requests.post(url, data=payload, timeout=15)

        if r.status_code != 200:
            print("Erro ao obter token:", r.status_code, r.text)
            return None

        return r.json().get("access_token")

    except Exception as e:
        print("Erro conexão token:", e)
        return None


def calcular_periodo():

    agora = datetime.now()
    dez_minutos = agora - timedelta(minutes=10)

    return {
        "dataI": dez_minutos.strftime("%d/%m/%Y"),
        "dataF": agora.strftime("%d/%m/%Y"),
        "horaI": dez_minutos.strftime("%H:%M"),
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


def coletar_sip_stats(nome_servidor, base_url):

    session = requests.Session()

    login(session, base_url)
    abrir_relatorio(session, base_url)

    periodo = calcular_periodo()
    rotas = pegar_rotas(session, base_url)

    resultados = []

    print(
        f"{nome_servidor} → Período: {periodo['dataI']} {periodo['horaI']} "
        f"→ {periodo['dataF']} {periodo['horaF']}"
    )

    print(f"Iniciando coleta sequencial: {nome_servidor}")

    for rota in rotas:

        dados = consultar_rota(session, base_url, rota, periodo)

        resultados.extend(dados)

        time.sleep(0.6)

    print(f"Coleta finalizada: {nome_servidor} → {len(resultados)} registros")

    return resultados

def coletar_servidores_paralelo(servidores):

    resultados = {}

    with ThreadPoolExecutor(max_workers=len(servidores)) as executor:

        futures = {
            executor.submit(coletar_sip_stats, nome, url): nome
            for nome, url in servidores.items()
        }

        for future in as_completed(futures):

            servidor = futures[future]

            try:

                resultado = future.result()

                if not resultado:
                    resultado = []

                resultados[servidor] = resultado

            except Exception as e:

                print(f"Erro no servidor {servidor}: {e}")

                resultados[servidor] = {
                    "erro": str(e)
                }

    return resultados


def enviar_email(html, assunto):

    token = obter_token()

    if not token:
        print("Token do Graph não obtido")
        return

    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_FROM}/sendMail"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    to_recipients = [
        {"emailAddress": {"address": email}}
        for email in EMAIL_TO
    ]

    body = {
        "message": {
            "subject": assunto,
            "body": {
                "contentType": "HTML",
                "content": html
            },
            "toRecipients": to_recipients
        },
        "saveToSentItems": "false"
    }

    try:

        r = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=20
        )

        if r.status_code not in (200, 202):

            print("Erro enviando email")
            print("Status:", r.status_code)
            print("Resposta:", r.text)

        else:

            print("Email enviado com sucesso")

    except Exception as e:

        print("Erro na requisição Graph:", e)
    
def analisar_sip(dados, servidor):
    if not dados:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(dados)

    df["quantidade"] = df["quantidade"].astype(int)

    df["sip_num"] = df["sip_code"].str.extract(r"(\d{3})")

    totais = df.groupby("rota")["quantidade"].sum().reset_index()
    totais.columns = ["rota", "total"]

    sip200 = df[df["sip_num"] == "200"].groupby("rota")["quantidade"].sum().reset_index()
    sip200.columns = ["rota", "completas"]

    resumo = totais.merge(sip200, on="rota", how="left").fillna(0)

    resumo["asr"] = (resumo["completas"] / resumo["total"]) * 100

    rotas_ruins = resumo[resumo["asr"] < LIMITE_COMPLETAMENTO]

    sip_dist = df.groupby(["rota","sip_num"])["quantidade"].sum().reset_index()

    sip_dist = sip_dist.merge(totais, on="rota")

    sip_dist["percentual"] = (sip_dist["quantidade"] / sip_dist["total"]) * 100

    return rotas_ruins, sip_dist

def gerar_html(rotas_ruins, sip_dist, servidor):

    html = f"""
    <html>
    <body style="font-family:Arial;background:#f5f7fa;padding:20px">

    <h2 style="color:#0a2b54">
    Relatório Monitoramento SIP - {servidor}
    </h2>

    <p>
    Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </p>

    <h3 style="background:#0094c1;color:white;padding:10px">
    Rotas com ASR abaixo de {LIMITE_COMPLETAMENTO}%
    </h3>

    <table style="border-collapse:collapse;width:100%">
    <tr style="background:#0a2b54;color:white">
        <th>Rota</th>
        <th>Total</th>
        <th>Completas</th>
        <th>ASR</th>
        <th>SIP</th>
    </tr>
    """

    if rotas_ruins.empty:

        html += f"""
        <tr style="background:#f0f0f0">
            <td colspan="5" style="text-align:center;padding:8px">
            Nenhuma rota com ASR abaixo de {LIMITE_COMPLETAMENTO}%
            </td>
        </tr>
        """

    else:

        for _, row in rotas_ruins.sort_values("asr", ascending=False).iterrows():

            rota = row["rota"]

            sip_rota = sip_dist[sip_dist["rota"] == rota]

            sip_texto = " | ".join(
                [
                    f"{s['sip_num']}: {s['percentual']:.1f}%"
                    for _, s in sip_rota.sort_values("percentual", ascending=False).iterrows()
                ]
            )

            html += f"""
            <tr style="background:#e9f6fb">
                <td>{rota}</td>
                <td>{int(row['total'])}</td>
                <td>{int(row['completas'])}</td>
                <td style="color:red;font-weight:bold">{row['asr']:.2f}%</td>
                <td>{sip_texto}</td>
            </tr>
            """

    html += "</table></body></html>"

    return html