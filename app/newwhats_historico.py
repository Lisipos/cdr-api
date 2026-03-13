import re
from bs4 import BeautifulSoup

BASE_URL = "https://newwhats.nvtelecom.com.br"


def buscar_historico_completo(session, first_day, last_day):

    # abrir página para pegar CSRF
    r = session.get(f"{BASE_URL}/historico", timeout=30)

    soup = BeautifulSoup(r.text, "html.parser")

    token = soup.find("input", {"name": "_token"})["value"]

    payload = {
        "_token": token,
        "_method": "post",
        "id_usuario": "0",
        "first_day": first_day,
        "last_day": last_day,
        "tarifa": "",
        "tarifa_v2": "",
        "v2": "3",

        # TRUQUE: pegar tudo de uma vez
        "length": "10000",
        "start": "0"
    }

    r = session.post(
        f"{BASE_URL}/historico",
        data=payload,
        timeout=60
    )

    if "login" in r.url.lower():
        raise Exception("Sessão expirou")

    soup = BeautifulSoup(r.text, "html.parser")

    linhas = soup.select("#table_id tbody tr")

    dados = []

    def limpar(texto):
        return re.sub(r"\s+", " ", texto).strip()
    
    for linha in linhas:

        colunas = [limpar(c.get_text()) for c in linha.find_all("td")]

        if len(colunas) < 11:
            continue

        dados.append({
            "id_campanha": colunas[0],
            "tipo": colunas[1],
            "nome": colunas[2],
            "centro_custo": colunas[3],
            "cliente": colunas[4],
            "registro": colunas[5],
            "arquivo": colunas[6],
            "envios": colunas[7],
            "blacklist": colunas[8],
            "erros": colunas[9],
            "valor": colunas[10]
        })

    # totais
    wpv1 = None
    wpv2 = None

    totais = soup.select("#table_id tfoot tr")

    if len(totais) >= 1:
        wpv1 = limpar(totais[0].get_text())

    if len(totais) >= 2:
        wpv2 = limpar(totais[1].get_text())

    return {
        "total_registros": len(dados),
        "wpv1_total": wpv1,
        "wpv2_total": wpv2,
        "dados": dados
    }