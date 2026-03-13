import re
from datetime import datetime
from bs4 import BeautifulSoup
from app.db import get_connection

BASE_URL = "https://newwhats.nvtelecom.com.br"


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def parse_valor(valor):
    valor = valor.replace("R$", "").strip()
    valor = valor.replace(".", "").replace(",", ".")
    return float(valor)


def parse_data(data_str):

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S"
    ]

    for formato in formatos:
        try:
            return datetime.strptime(data_str, formato)
        except ValueError:
            continue

    raise ValueError(f"Formato de data desconhecido: {data_str}")


def carregar_tipos(cursor):

    cursor.execute("""
        SELECT id_whats_tb_tipo, tipo
        SELECT id_whats_tb_tipo, tipo
        FROM whats_tb_tipo
    """)

    return {tipo.strip(): tid for tid, tipo in cursor.fetchall()}
    return {tipo.strip(): tid for tid, tipo in cursor.fetchall()}


def buscar_historico(session, first_day, last_day):

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
        "length": "100000",
        "start": "0"
    }

    r = session.post(
        f"{BASE_URL}/historico",
        data=payload,
        timeout=60
    )

    return BeautifulSoup(r.text, "html.parser")


def salvar_historico_mysql_lote(session, first_day, last_day):

    conn = get_connection()
    cursor = conn.cursor()

    tipos = carregar_tipos(cursor)

    start = 0
    total_registros = 0

    # proteção contra repetição
    ids_processados = set()
    ultimo_primeiro_id = None

    while True:

        soup = buscar_historico(session, first_day, last_day, start)

    linhas = soup.select("#table_id tbody tr")

        if not linhas:
            print("Nenhuma linha encontrada.")
            break

    dados = []
    total_registros = 0

    for linha in linhas:

        colunas = [limpar(c.get_text()) for c in linha.find_all("td")]

        if len(colunas) < 11:
            continue

        try:

                id_campanha = int(colunas[0])

                # evita reprocessar
                if id_campanha in ids_processados:
                    continue

                ids_processados.add(id_campanha)

                tipo_nome = colunas[1]
                nome = colunas[2]
                centro_custo = colunas[3]

                id_tipo = tipos.get(tipo_nome)

            registro = parse_data(colunas[5])

            arquivo = int(colunas[6])
            envios = int(colunas[7])
            blacklist = int(colunas[8])
            erros = int(colunas[9])
            valor = parse_valor(colunas[10])

            status = colunas[11] if len(colunas) > 11 else "Finalizada"

                dados.append((
                    id_campanha,
                    id_tipo,
                    nome,
                    centro_custo,
                    registro,
                    arquivo,
                    envios,
                    blacklist,
                    erros,
                    valor,
                    status
                ))

        except Exception as e:

            print("Erro linha:", colunas, e)

        if not dados:
            print("Nenhum registro novo encontrado. Encerrando.")
            break

        primeiro_id_pagina = dados[0][0]

        # detecta página repetida
        if primeiro_id_pagina == ultimo_primeiro_id:
            print("Página repetida detectada. Encerrando paginação.")
            break

        ultimo_primeiro_id = primeiro_id_pagina

        sql = """
        INSERT INTO whats_tb_historico
        (id_campanha,id_tipo,nome,centro_custo,registro,arquivo,envios,blacklist,erros,valor,status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        ON DUPLICATE KEY UPDATE
            id_tipo=VALUES(id_tipo),
            nome=VALUES(nome),
            centro_custo=VALUES(centro_custo),
            registro=VALUES(registro),
            arquivo=VALUES(arquivo),
            envios=VALUES(envios),
            blacklist=VALUES(blacklist),
            erros=VALUES(erros),
            valor=VALUES(valor),
            status=VALUES(status)
        """

    batch_size = 5000

    for i in range(0, len(dados), batch_size):

        lote = dados[i:i + batch_size]

        cursor.executemany(sql, lote)

        conn.commit()

        total_registros += len(lote)

        print(f"Página {start} → {len(dados)} registros")

        # proteção se o portal ignorar start
        if len(linhas) < 1000:
            print("Última página detectada.")
            break

        start += 1000

    cursor.close()
    conn.close()

    print(f"Total processado: {total_registros}")

    return total_registros