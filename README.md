# 📦 CDR API

API para geração e exportação de CDRs em formato ZIP utilizando processamento assíncrono com Celery.

---

## 🚀 Tecnologias

- FastAPI
- Celery
- Redis
- Docker
- Python 3.11

---

## 🏗 Arquitetura

Cliente → FastAPI → Celery → API Externa (CDR) → Geração de ZIP → Download

---

## ⚙️ Configuração

### 1️⃣ Criar arquivo `.env`

Copie o arquivo `.env.example`:

cp .env.example .env

Edite com suas credenciais:
EXTERNAL_API_TOKEN=seu_token_externo
EXTERNAL_API_KEY=sua_api_key_externa
INTERNAL_API_TOKEN=seu_token_interno

---

## 🐳 Executando com Docker

```bash
docker compose up --build
```
A API estará disponível em:

http://localhost:8000

## 🔐 Autenticação

Todas as rotas exigem header:

Authorization: Bearer SEU_INTERNAL_API_TOKEN

## 📡 Endpoints
🔹 Gerar CDR

POST /gerar-cdr

Body JSON:

{
  "date_ini": "2026-02-12",
  "date_end": "2026-02-12",
  "time_ini": "00:00:00",
  "time_end": "23:59:59",
  "start": 0,
  "limit": 1000,
  "device_id": 7389
}


Retorno:

{
  "job_id": "uuid-gerado"
}

🔹 Consultar Status

GET /status/{job_id}

🔹 Download do ZIP

GET /download/{job_id}

Retorna o arquivo .zip gerado.

## 📂 Estrutura do Projeto
app/
 ├── main.py
 ├── tasks.py
 ├── cdr_service.py
 ├── config.py
 ├── security.py
 └── models.py
docker-compose.yml
Dockerfile
requirements.txt

## 📌 Observações

Processamento assíncrono via Celery

Redis como broker e backend

Tokens e credenciais nunca devem ser versionados

Utilize .env para variáveis sensíveis

## 👨‍💻 Autor

Felipe Uglar