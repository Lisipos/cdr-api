import re
from bs4 import BeautifulSoup
from app.db import get_connection

BASE_URL = "https://newwhats.nvtelecom.com.br"


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def parse_valor(valor):

    valor = valor.replace("R$", "").strip()
    valor = valor.replace(".", "").replace(",", ".")

    return float(valor)


def salvar_historico_mysql_lote(session, first_day, last_day):

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
        "length": "10000",
        "start": "0"
    }

    r = session.post(
        f"{BASE_URL}/historico",
        data=payload,
        timeout=60
    )

    soup = BeautifulSoup(r.text, "html.parser")

    linhas = soup.select("#table_id tbody tr")

    dados = []

    for linha in linhas:

        colunas = [limpar(c.get_text()) for c in linha.find_all("td")]

        if len(colunas) < 11:
            continue

        dados.append((
            int(colunas[0]),
            colunas[1],
            colunas[2],
            colunas[3],
            colunas[4],
            colunas[5],
            int(colunas[6]),
            int(colunas[7]),
            int(colunas[8]),
            int(colunas[9]),
            parse_valor(colunas[10]),
            colunas[11] if len(colunas) > 11 else "Finalizada"
        ))

    if not dados:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO whats_tb_historico
    (id_campanha,id_tipo,nome,centro_custo,id_cliente,registro,arquivo,envios,blacklist,erros,valor,status)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        tipo=VALUES(tipo),
        nome=VALUES(nome),
        centro_custo=VALUES(centro_custo),
        cliente=VALUES(cliente),
        registro=VALUES(registro),
        arquivo=VALUES(arquivo),
        envios=VALUES(envios),
        blacklist=VALUES(blacklist),
        erros=VALUES(erros),
        valor=VALUES(valor),
        status=VALUES(status)
    """

    cursor.executemany(sql, dados)

    conn.commit()

    total = cursor.rowcount

    cursor.close()
    conn.close()

    return total