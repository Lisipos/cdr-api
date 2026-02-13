import httpx
import os
import csv
import zipfile
from datetime import datetime
from app.config import get_api_url, OUTPUT_DIR
# import win32com.client as win32

def gerar_cdr_zip(
    date_ini,
    date_end,
    time_ini="",
    time_end="",
    device_id=None
):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{OUTPUT_DIR}/cdr_{timestamp}.csv"
    zip_filename = f"{OUTPUT_DIR}/cdr_{timestamp}.zip"

    start = 0
    limit = 1000
    primeiro_bloco = True

    api_url = get_api_url()

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:

        writer = None

        while True:

            params = {
                "date_ini": date_ini,
                "date_end": date_end,
                "time_ini": time_ini,
                "time_end": time_end,
                "start": start,
                "limit": limit
            }

            if device_id:
                params["device_id"] = device_id

            response = httpx.get(api_url, params=params, timeout=120.0)

            if response.status_code != 200:
                raise Exception(f"Erro HTTP: {response.status_code}")

            dados = response.json()

            if dados.get("error") != 0:
                raise Exception(dados.get("reason"))

            registros = dados.get("data", [])

            if not registros:
                break

            if primeiro_bloco:
                writer = csv.DictWriter(csv_file, fieldnames=registros[0].keys())
                writer.writeheader()
                primeiro_bloco = False

            for row in registros:
                writer.writerow(row)

            print(f"Baixados {start + len(registros)} registros...")

            start += limit

            if start >= dados.get("total_records", 0):
                break

    # Compactar
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_filename, os.path.basename(csv_filename))

    os.remove(csv_filename)

    return zip_filename


