from fastapi import Depends
from app.security import verificar_token
from fastapi import FastAPI
from fastapi import HTTPException
from app.tasks import processar_cdr
from celery.result import AsyncResult
from fastapi.responses import FileResponse
from app.models import CDRRequest
from app.tasks import celery_app
import os
from celery.schedules import crontab
from app.tasks import task_coletar_sip
from app.sip_collect import coletar_sip_stats
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config import SERVIDORES

app = FastAPI()
# app = FastAPI(dependencies=[Depends(verificar_token)])

@app.post("/coletar-sip")
def coletar_sip_manual():

    task = task_coletar_sip.delay()

    return {
        "job_id": task.id,
        "status": "processando"
    }




# @app.get("/sip-report")
# def sip_report():

#     resultado = {}

#     with ThreadPoolExecutor(max_workers=3) as executor:

#         futures = {
#             executor.submit(coletar_sip_stats, url): nome
#             for nome, url in SERVIDORES.items()
#         }

#         for future in as_completed(futures):

#             nome = futures[future]

#             try:

#                 resultado[nome] = future.result()

#             except Exception as e:

#                 resultado[nome] = {"erro": str(e)}

#     return resultado

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

    # 1️⃣ Verifica se existe
    if not task:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    # 2️⃣ Verifica status
    if task.status != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"Job ainda não finalizado. Status atual: {task.status}"
        )

    # 3️⃣ Pega caminho retornado pela task
    file_path = task.result

    # 4️⃣ Verifica se arquivo existe
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/zip"
    )