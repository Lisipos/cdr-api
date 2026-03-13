from celery import Celery
from app.cdr_service import gerar_cdr_zip
from app.config import REDIS_URL, SERVIDORES, LIMITE_COMPLETAMENTO, EMAIL_WHATS, PASSWORD_WHATS, EMAIL_WHATS, PASSWORD_WHATS
from celery.schedules import crontab
from app.sip_collect import (
    coletar_servidores_paralelo,
    analisar_sip,
    gerar_html,
    enviar_email
)
from datetime import datetime, timedelta
from app.newwhats_auth import login_newwhats
from app.newwhats_csv import baixar_csv_historico
from app.newwhats_db import salvar_historico_mysql_lote


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

@celery_app.task(name="task_newwhats_csv")
def task_newwhats_csv():

    ontem = datetime.now() - timedelta(days=1)

    inicio = ontem.replace(hour=0, minute=0, second=0)
    fim = ontem.replace(hour=23, minute=59, second=59)

    session = login_newwhats(EMAIL_WHATS, PASSWORD_WHATS)

    path = baixar_csv_historico(
        session,
        inicio.strftime("%Y-%m-%dT%H:%M"),
        fim.strftime("%Y-%m-%dT%H:%M"),
        f"historico_{ontem.strftime('%Y%m%d')}.csv"
    )

    print(f"CSV gerado: {path}")

@celery_app.task(name="task_coletar_newwhats_mysql")
def task_coletar_newwhats_mysql():

    ontem = datetime.now() - timedelta(days=1)

    first_day = ontem.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M")
    last_day = ontem.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M")

    print(f"Coletando histórico NewWhats {first_day} -> {last_day}")

    session = login_newwhats(EMAIL_WHATS, PASSWORD_WHATS)

    total = salvar_historico_mysql_lote(session, first_day, last_day)

    print(f"Registros processados: {total}")

    return {
        "periodo": f"{first_day} -> {last_day}",
        "registros": total
    }



celery_app.conf.beat_schedule = {
    "monitor-sip-cada-1-h": {
        "task": "task_coletar_sip",
        "schedule": crontab(minute=0),
    },
    # "newwhats-csv-meia-noite": {
    #     "task": "task_newwhats_csv",
    #     "schedule": crontab(hour=0, minute=5)
    # },
    "coletar-newwhats-diario": {
        "task": "task_coletar_newwhats_mysql",
        "schedule": crontab(hour=0, minute=5)
    }
}
