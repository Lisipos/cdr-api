# tasks.py
from celery import Celery
from app.cdr_service import gerar_cdr_zip
from app.config import REDIS_URL
from celery.schedules import crontab
from app.sip_collect import coletar_sip_stats  # versão atualizada
import csv
import os
from datetime import datetime

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)


@celery_app.task
def processar_cdr(date_ini, date_end, time_ini, time_end, device_id):
    return gerar_cdr_zip(date_ini, date_end, time_ini, time_end, device_id)


@celery_app.task(name="app.sip_stats.task_coletar_sip")
def task_coletar_sip():
    # coletar_sip_stats retorna uma lista de dicts
    dados = coletar_sip_stats()
    if not dados:
        return "Sem dados"

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/sip_stats_{agora}.csv"

    # escreve CSV usando dicionários
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # cabeçalho
        writer.writerow(["timestamp", "rota_id", "rota_nome", "sip_code", "quantidade"])
        for d in dados:
            writer.writerow([d["timestamp"], d["rota_id"], d["rota_nome"], d["sip_code"], d["quantidade"]])

    return file_path


# celery_app.conf.beat_schedule = {
#     "coletar-sip-cada-1h": {
#         "task": "app.sip_stats.task_coletar_sip",
#         "schedule": crontab(minute=0),
#     }
# }