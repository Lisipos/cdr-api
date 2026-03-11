from celery import Celery
from app.cdr_service import gerar_cdr_zip
from app.config import REDIS_URL
from celery.schedules import crontab
from app.sip_collect import (
    coletar_servidores_paralelo,
    analisar_sip,
    gerar_html,
    enviar_email
)
from app.config import SERVIDORES, LIMITE_COMPLETAMENTO


celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)


@celery_app.task
def processar_cdr(date_ini, date_end, time_ini, time_end, device_id):
    return gerar_cdr_zip(date_ini, date_end, time_ini, time_end, device_id)


@celery_app.task(name="task_coletar_sip")
def task_coletar_sip():

    try:

        dados_servidores = coletar_servidores_paralelo(SERVIDORES)

        for nome, dados in dados_servidores.items():

            if isinstance(dados, dict) and "erro" in dados:
                print(f"Erro no servidor {nome}: {dados['erro']}")
                continue

            if not dados:
                print(f"Sem dados para {nome}")
                dados = []

            rotas_ruins, sip_dist = analisar_sip(dados, nome)

            html = gerar_html(rotas_ruins, sip_dist, nome)

            assunto = f"Monitor SIP - {nome} - ASR abaixo de {LIMITE_COMPLETAMENTO}%"

            try:
                enviar_email(html, assunto)
            except Exception as e:
                print(f"Erro enviando email {nome}: {e}")

        print("Monitor SIP finalizado")

    except Exception as e:

        print(f"Erro na task SIP: {e}")


celery_app.conf.beat_schedule = {
    "monitor-sip-cada-10-min": {
        "task": "task_coletar_sip",
        "schedule": crontab(minute="*/10"),
    }
}