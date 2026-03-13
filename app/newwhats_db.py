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
    return datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")


def carregar_clientes(cursor):

    cursor.execute("""
        SELECT id_whats_tb_cliente, nome
        FROM whats_tb_cliente
    """)

    return {nome.strip(): cid for cid, nome in cursor.fetchall()}


def carregar_tipos(cursor):

    cursor.execute("""
        SELECT id_whats_tb_tipo, nome
        FROM whats_tb_tipo
    """)

    return {nome.strip(): tid for tid, nome in cursor.fetchall()}


def buscar_historico(session, first_day, last_day, start):

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
        "length": "1000",
        "start": str(start)
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

    clientes = carregar_clientes(cursor)
    tipos = carregar_tipos(cursor)

    start = 0
    total_registros = 0

    while True:

        soup = buscar_historico(session, first_day, last_day, start)

        linhas = soup.select("#table_id tbody tr")

        if not linhas:
            break

        dados = []

        for linha in linhas:

            colunas = [limpar(c.get_text()) for c in linha.find_all("td")]

            if len(colunas) < 11:
                continue

            try:

                id_campanha = int(colunas[0])
                tipo_nome = colunas[1]
                nome = colunas[2]
                centro_custo = colunas[3]
                cliente_nome = colunas[4]

                id_tipo = tipos.get(tipo_nome)
                id_cliente = clientes.get(cliente_nome)

                if not id_cliente:
                    print(f"Cliente não encontrado: {cliente_nome}")
                    continue

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
                    id_cliente,
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
            break

        sql = """
        INSERT INTO whats_tb_historico
        (id_campanha,id_tipo,nome,centro_custo,id_cliente,registro,arquivo,envios,blacklist,erros,valor,status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        ON DUPLICATE KEY UPDATE
            id_tipo=VALUES(id_tipo),
            nome=VALUES(nome),
            centro_custo=VALUES(centro_custo),
            id_cliente=VALUES(id_cliente),
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

        total_registros += len(dados)

        print(f"Página {start} → {len(dados)} registros")

        if len(linhas) < 1000:
            break

        start += 1000

    cursor.close()
    conn.close()

    print(f"Total processado: {total_registros}")

    return total_registros