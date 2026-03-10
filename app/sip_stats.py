from app.tasks import celery_app
from app.sip_collect import coletar_sip_stats

@celery_app.task
def task_coletar_sip():
    return coletar_sip_stats()