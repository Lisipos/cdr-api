# 📦 CDR API

API para geração e exportação de CDRs em formato ZIP utilizando processamento assíncrono com Celery.
O projeto também inclui automações para monitoramento SIP e coleta de histórico de campanhas do NewWhats com armazenamento em banco de dados.

---

# 🚀 Tecnologias

* Python 3.11
* FastAPI
* Celery
* Redis
* Docker
* MySQL
* BeautifulSoup
* Requests

---

# 🏗 Arquitetura

CDR:

Cliente → FastAPI → Celery → API Externa (CDR) → Geração de ZIP → Download

Monitor SIP:

Celery Beat → Coleta servidores SIP → Análise de ASR → Geração HTML → Envio de Email

NewWhats:

Celery Beat → Login no portal → Coleta histórico → Download CSV / Parsing → Armazenamento MySQL

---

# ⚙️ Configuração

## 1️⃣ Criar arquivo `.env`

Copie o arquivo `.env.example`:

cp .env.example .env

Edite com suas credenciais:

EXTERNAL_API_TOKEN=seu_token_externo
EXTERNAL_API_KEY=sua_api_key_externa
INTERNAL_API_TOKEN=seu_token_interno

Configuração Redis:

REDIS_URL=redis://redis:6379/0

Configuração MySQL:

MYSQL_HOST=mysql
MYSQL_USER=usuario
MYSQL_PASSWORD=senha
MYSQL_DATABASE=cdr

Credenciais NewWhats:

EMAIL_WHATS=seu_email
PASSWORD_WHATS=sua_senha

---

# 🐳 Executando com Docker

```bash
docker compose up --build
```

A API estará disponível em:

http://localhost:8000

---

# 🔐 Autenticação

Todas as rotas exigem header:

Authorization: Bearer SEU_INTERNAL_API_TOKEN

---

# 📡 Endpoints

## 🔹 Gerar CDR

POST /gerar-cdr

Body JSON:

```
{
  "date_ini": "2026-02-12",
  "date_end": "2026-02-12",
  "time_ini": "00:00:00",
  "time_end": "23:59:59",
  "start": 0,
  "limit": 1000,
  "device_id": 7389
}
```

Retorno:

```
{
  "job_id": "uuid-gerado"
}
```

---

## 🔹 Consultar Status da Task

GET /status/{job_id}

Retorna o status da task no Celery.

---

## 🔹 Download do ZIP

GET /download/{job_id}

Retorna o arquivo `.zip` contendo os CDRs processados.

---

## 🔹 Download do CSV do histórico NewWhats

Endpoint que realiza login automático no portal NewWhats e gera o CSV do histórico de campanhas.

GET /newwhats/csv

Retorna o arquivo CSV gerado.

---

## 🔹 Consultar histórico NewWhats armazenado

GET /newwhats/historico

Consulta os dados previamente coletados e armazenados no banco MySQL.

---

# ⏰ Automação com Celery Beat

O sistema executa tarefas automáticas:

Monitor SIP:

Executa a cada 20 minutos

Funções:

* coleta dados dos servidores SIP
* calcula ASR
* detecta rotas com baixa completamento
* envia relatório por email

Coleta NewWhats:

Executa diariamente às 00:05

Funções:

* login automático no portal
* coleta histórico do dia anterior
* parsing dos dados
* inserção em lote no MySQL

---

# 🗄 Banco de Dados

Tabela utilizada para armazenar histórico de campanhas:

```
CREATE TABLE newwhats_historico (
    id_campanha BIGINT PRIMARY KEY,
    tipo VARCHAR(100),
    nome VARCHAR(255),
    centro_custo VARCHAR(255),
    cliente VARCHAR(255),
    registro DATETIME,
    arquivo INT,
    envios INT,
    blacklist INT,
    erros INT,
    valor DECIMAL(12,5)
);
```

A inserção utiliza:

* bulk insert (`executemany`)
* `ON DUPLICATE KEY UPDATE` para evitar duplicidade

---

# 📂 Estrutura do Projeto

```
app/
 ├── main.py
 ├── tasks.py
 ├── config.py
 ├── security.py
 ├── models.py
 ├── cdr_service.py
 ├── sip_collect.py
 ├── newwhats_auth.py
 ├── newwhats_csv.py
 ├── newwhats_db.py
 └── db.py

docker-compose.yml
Dockerfile
requirements.txt
```

---

# 📌 Observações

* Processamento assíncrono via Celery
* Redis utilizado como broker e backend
* Tasks automáticas via Celery Beat
* Coleta automatizada do portal NewWhats
* Inserção em lote no banco para melhor performance
* Tokens e credenciais nunca devem ser versionados
* Utilize `.env` para variáveis sensíveis

---

## 🚀 Deploy no Ubuntu

A seguir estão os passos para subir a aplicação em um servidor **Ubuntu** utilizando Docker.

---

### 1️⃣ Atualizar o sistema

```bash
sudo apt update && sudo apt upgrade -y
```

---

### 2️⃣ Instalar Docker

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

Verifique a instalação:

```bash
docker --version
```

---

### 3️⃣ Instalar Docker Compose

```bash
sudo apt install -y docker-compose-plugin
```

Verifique:

```bash
docker compose version
```

---

### 4️⃣ Clonar o repositório

```bash
git clone https://seu-repositorio.git
cd CDR-API
```

---

### 5️⃣ Criar o arquivo `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o arquivo:

```bash
nano .env
```

Configure suas credenciais:

```
EXTERNAL_API_TOKEN=seu_token_externo
EXTERNAL_API_KEY=sua_api_key_externa
INTERNAL_API_TOKEN=seu_token_interno

REDIS_URL=redis://redis:6379/0

MYSQL_HOST=mysql
MYSQL_USER=usuario
MYSQL_PASSWORD=senha
MYSQL_DATABASE=cdr

EMAIL_WHATS=seu_email
PASSWORD_WHATS=sua_senha
```

---

### 6️⃣ Subir os containers

```bash
docker compose up -d --build
```

Isso irá iniciar:

* API (FastAPI)
* Worker Celery
* Celery Beat (agendador de tarefas)
* Redis (broker do Celery)

---

### 7️⃣ Verificar containers

```bash
docker ps
```

---

### 8️⃣ Ver logs

Logs da API:

```bash
docker compose logs -f api
```

Logs do worker Celery:

```bash
docker compose logs -f worker
```

Logs do scheduler:

```bash
docker compose logs -f beat
```

---

### 9️⃣ Acessar a API

A API ficará disponível em:

```
http://IP_DO_SERVIDOR:8000
```

Documentação automática do FastAPI:

```
http://IP_DO_SERVIDOR:8000/docs
```

---

### 🔄 Atualizar aplicação

Quando houver alterações no código:

```bash
git pull
docker compose up -d --build
```

---

### 🛑 Parar a aplicação

```bash
docker compose down
```

---

### 📌 Executar automaticamente ao iniciar o servidor (opcional)

Para garantir que os containers iniciem após reboot:

```bash
sudo systemctl enable docker
```

E utilize no `docker-compose.yml`:

```
restart: always
```

# 👨‍💻 Autor

Felipe Uglar
