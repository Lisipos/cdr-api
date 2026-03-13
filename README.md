# 📦 CDR API

API para **geração, processamento e exportação de CDRs** em formato `.zip` utilizando **processamento assíncrono com Celery**.

O sistema também inclui automações para:

* Monitoramento de rotas **SIP**
* Coleta automática de histórico de campanhas **NewWhats**
* Armazenamento estruturado em **MySQL**

---

# 🚀 Tecnologias

| Tecnologia    | Uso                      |
| ------------- | ------------------------ |
| Python 3.11   | Backend                  |
| FastAPI       | API REST                 |
| Celery        | Processamento assíncrono |
| Redis         | Broker de filas          |
| Docker        | Containerização          |
| MySQL         | Persistência de dados    |
| BeautifulSoup | Parsing HTML             |
| Requests      | Integrações HTTP         |

---

# 🏗 Arquitetura

## 📊 Geração de CDR

Fluxo:

```
Cliente
   │
   ▼
FastAPI
   │
   ▼
Celery Worker
   │
   ▼
API Externa (CDR)
   │
   ▼
Processamento
   │
   ▼
ZIP gerado
   │
   ▼
Download
```

---

## 📡 Monitoramento SIP

```
Celery Beat
   │
   ▼
Coleta servidores SIP
   │
   ▼
Análise ASR
   │
   ▼
Detecção rotas problemáticas
   │
   ▼
Relatório HTML
   │
   ▼
Envio por Email
```

---

## 📈 Coleta NewWhats

```
Celery Beat
   │
   ▼
Login portal NewWhats
   │
   ▼
Coleta histórico campanhas
   │
   ▼
Download CSV
   │
   ▼
Parsing dados
   │
   ▼
Armazenamento MySQL
```

---

# ⚙️ Configuração

## 1️⃣ Criar arquivo `.env`

Copie o arquivo de exemplo:

```
cp .env.example .env
```

Edite o arquivo com suas credenciais.

---

## 🔐 Tokens da API

```
EXTERNAL_API_TOKEN=seu_token_externo
EXTERNAL_API_KEY=sua_api_key_externa
INTERNAL_API_TOKEN=seu_token_interno
```

---

## 🔁 Redis

```
REDIS_URL=redis://redis:6379/0
```

---

## 🗄 MySQL

```
MYSQL_HOST=mysql
MYSQL_USER=usuario
MYSQL_PASSWORD=senha
MYSQL_DATABASE=cdr
```

---

## 📲 Credenciais NewWhats

```
EMAIL_WHATS=seu_email
PASSWORD_WHATS=sua_senha
```

---

# 🐳 Executando com Docker

Subir aplicação:

```
docker compose up --build
```

A API ficará disponível em:

```
http://localhost:8000
```

---

# 🔐 Autenticação

Todas as rotas exigem header:

```
Authorization: Bearer SEU_INTERNAL_API_TOKEN
```

---

# 📡 Endpoints

## 🔹 Gerar CDR

**POST**

```
/gerar-cdr
```

### Body

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

### Resposta

```
{
  "job_id": "uuid-gerado"
}
```

---

## 🔹 Consultar status da task

```
GET /status/{job_id}
```

Retorna o status da task no Celery.

---

## 🔹 Download do ZIP

```
GET /download/{job_id}
```

Retorna o arquivo `.zip` contendo os CDRs processados.

---

## 🔹 Download CSV histórico NewWhats

```
GET /newwhats/csv
```

Executa login automático no portal **NewWhats** e gera o CSV do histórico.

---

## 🔹 Consultar histórico armazenado

```
GET /newwhats/historico
```

Consulta dados armazenados previamente no banco **MySQL**.

---

# ⏰ Automação com Celery Beat

O sistema executa tarefas automáticas.

---

## 📡 Monitor SIP

Executa **a cada 20 minutos**.

Funções:

* coleta dados dos servidores SIP
* calcula **ASR**
* detecta rotas com baixo completamento
* envia relatório por email

---

## 📊 Coleta NewWhats

Executa **diariamente às 00:05**.

Funções:

* login automático no portal
* coleta histórico do dia anterior
* parsing do CSV
* inserção em lote no banco

---

# 🗄 Banco de Dados

Tabela utilizada para armazenar histórico de campanhas.

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

---

## Estratégia de inserção

* **bulk insert** (`executemany`)
* `ON DUPLICATE KEY UPDATE`
* evita duplicidade
* melhora performance

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

* Processamento assíncrono via **Celery**
* **Redis** utilizado como broker
* Agendamento via **Celery Beat**
* Automação do portal **NewWhats**
* Inserção em lote no banco para alta performance
* Credenciais devem ficar apenas em `.env`

---

# 🚀 Deploy no Ubuntu

## 1️⃣ Atualizar sistema

```
sudo apt update && sudo apt upgrade -y
```

---

## 2️⃣ Instalar Docker

```
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

Verificar:

```
docker --version
```

---

## 3️⃣ Instalar Docker Compose

```
sudo apt install -y docker-compose-plugin
```

Verificar:

```
docker compose version
```

---

## 4️⃣ Clonar repositório

```
git clone https://seu-repositorio.git
cd CDR-API
```

---

## 5️⃣ Criar `.env`

```
cp .env.example .env
nano .env
```

---

## 6️⃣ Subir containers

```
docker compose up -d --build
```

Containers iniciados:

* API
* Celery Worker
* Celery Beat
* Redis

---

## 7️⃣ Verificar containers

```
docker ps
```

---

## 8️⃣ Ver logs

API:

```
docker compose logs -f api
```

Worker:

```
docker compose logs -f worker
```

Scheduler:

```
docker compose logs -f beat
```

---

## 9️⃣ Acessar API

```
http://IP_DO_SERVIDOR:8000
```

Documentação automática:

```
http://IP_DO_SERVIDOR:8000/docs
```

---

# 🔄 Atualizar aplicação

```
git pull
docker compose up -d --build
```

---

# 🛑 Parar aplicação

```
docker compose down
```

---

# 📌 Inicializar automaticamente após reboot

No `docker-compose.yml`:

```
restart: always
```

---

# 👨‍💻 Autor

**Felipe Uglar**
