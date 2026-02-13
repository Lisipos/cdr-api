from celery import Celery
from app.cdr_service import gerar_cdr_zip
from app.config import REDIS_URL

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)


@celery_app.task
def processar_cdr(date_ini, date_end, time_ini, time_end, device_id):
    return gerar_cdr_zip(
        date_ini,
        date_end,
        time_ini,
        time_end,
        device_id
    )
