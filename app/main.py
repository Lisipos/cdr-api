from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
import os

from app.models import CDRRequest
from app.tasks import processar_cdr, celery_app, task_coletar_sip
from app.config import EMAIL_WHATS, PASSWORD_WHATS
from app.newwhats_auth import login_newwhats
from app.newwhats_historico import buscar_historico_completo
from app.newwhats_csv import baixar_csv_historico
from app.newwhats_db import salvar_historico_mysql_lote
from app.db import get_connection

app = FastAPI()


@app.post("/coletar-sip")
def coletar_sip_manual():

    task = task_coletar_sip.delay()

    return {
        "job_id": task.id,
        "status": "processando"
    }


@app.get("/newwhats/login")
def login():

    session = login_newwhats(EMAIL_WHATS, PASSWORD_WHATS)

    r = session.get(
        "https://newwhats.nvtelecom.com.br/dashboard",
        timeout=30
    )

    return {
        "status": "logado",
        "dashboard_status": r.status_code
    }


@app.get("/newwhats/historico")
def historico():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM newwhats_historico
        ORDER BY registro DESC
        LIMIT 100
    """)

    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados


@app.get("/newwhats/historico/csv")
def historico_csv():

    session = login_newwhats(EMAIL_WHATS, PASSWORD_WHATS)

    try:

        file_path = baixar_csv_historico(
            session,
            "2026-03-01T00:00",
            "2026-03-12T23:59"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Erro gerando CSV: {str(e)}"
        )

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=os.path.basename(file_path)
    )


@app.get("/newwhats/historico/mysql")
def historico_mysql():

    session = login_newwhats(EMAIL_WHATS, PASSWORD_WHATS)

    total = salvar_historico_mysql_lote(
        session,
        "2026-03-11T00:00",
        "2026-03-11T23:59"
    )

    return {
        "status": "ok",
        "registros_processados": total
    }


@app.post("/gerar-cdr")
def gerar(dados: CDRRequest):

    task = processar_cdr.delay(
        dados.date_ini,
        dados.date_end,
        dados.time_ini,
        dados.time_end,
        dados.device_id
    )

    return {"job_id": task.id}


@app.get("/status/{job_id}")
def status(job_id: str):

    task = AsyncResult(job_id, app=celery_app)

    return {
        "job_id": job_id,
        "status": task.status,
        "result": task.result
    }


@app.get("/download/{job_id}")
def download(job_id: str):

    task = AsyncResult(job_id, app=celery_app)

    if task.status != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"Job ainda não finalizado. Status: {task.status}"
        )

    file_path = task.result

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/zip"
    )
    
    # Gabriel Costa