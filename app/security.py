from fastapi import Header, HTTPException
import os

API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

def verificar_token(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Token não informado")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato inválido")

    token = authorization.split(" ")[1]

    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

    return True