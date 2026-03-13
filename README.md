# CDR API – Processamento e Armazenamento de Relatórios

API desenvolvida em **Python (FastAPI)** para coleta, processamento e armazenamento de relatórios CDR, com execução assíncrona utilizando **Celery + Redis** e deploy via **Docker**.

O sistema permite automatizar a coleta de relatórios, processar arquivos e salvar os dados diretamente em um banco **MySQL**.

---

# Arquitetura do Sistema

```
            ┌─────────────┐
            │   Cliente   │
            │  (API Call) │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │   FastAPI   │
            │    (API)    │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │    Redis    │
            │  (Broker)   │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │   Celery    │
            │   Worker    │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │   MySQL     │
            │  Database   │
            └─────────────┘
```

---

# Tecnologias Utilizadas

| Tecnologia | Função                   |
| ---------- | ------------------------ |
| FastAPI    | API REST                 |
| Celery     | Processamento assíncrono |
| Redis      | Broker de tarefas        |
| MySQL      | Armazenamento de dados   |
| Docker     | Containerização          |
| Uvicorn    | Servidor ASGI            |

---

# Estrutura do Projeto

```
cdr-api
│
├── app
│   ├── main.py           # API principal
│   ├── tasks.py          # Tasks do Celery
│   ├── database.py       # Conexão com banco
│   ├── models.py         # Estrutura das tabelas
│   └── config.py         # Configurações do sistema
│
├── exports               # Relatórios exportados
├── output                # Arquivos processados
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# Estrutura da Tabela MySQL

Tabela utilizada para armazenar os dados processados:

```sql
CREATE TABLE campanhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_campanha VARCHAR(50),
    tipo VARCHAR(50),
    nome VARCHAR(255),
    centro_custo VARCHAR(100),
    cliente VARCHAR(100),
    registro DATETIME,
    arquivo VARCHAR(255),
    envios INT,
    blacklist INT,
    erros INT,
    valor DECIMAL(10,2)
);
```

---

# Endpoint da API

## Processar relatórios

```
POST /processar
```

Esse endpoint:

1. Lê os arquivos de relatório
2. Processa os dados
3. Salva no banco MySQL
4. Executa o processamento em background com Celery

---

# Execução com Docker

## 1. Build do projeto

```
docker compose build
```

---

## 2. Subir os containers

```
docker compose up -d
```

---

## 3. Ver containers rodando

```
docker ps
```

Containers esperados:

```
api
worker
beat
redis
```

---

# Acessar API

Após subir o projeto:

```
http://IP_DO_SERVIDOR:8000/docs
```

Interface automática do **FastAPI**.

---

# Agendamentos Automáticos

O sistema utiliza **Celery Beat** para executar tarefas programadas.

### Executar processamento diariamente

```
00:00
```

Configuração:

```python
crontab(hour=0, minute=0)
```

---

# Deploy no Servidor

## Clonar projeto

```
git clone https://seu-repositorio.git
cd cdr-api
```

---

## Subir containers

```
docker compose up -d --build
```

---

## Atualizar versão

Quando houver nova versão:

```
git pull
docker compose down
docker compose up -d --build
```

---

# Padrão de Branches

| Branch  | Função          |
| ------- | --------------- |
| main    | Produção        |
| develop | Desenvolvimento |

Branches auxiliares:

```
feature/nova-funcionalidade
fix/correcao-bug
hotfix/correcao-producao
docs/documentacao
```

---

# Padrão de Commits

Formato utilizado:

```
tipo: descrição
```

Exemplos:

```
feat: adiciona salvamento de campanhas no MySQL
fix: corrige erro de schedule celery
build: adiciona docker-compose
docs: adiciona guia de deploy
```

Tipos de commit:

| Tipo     | Uso                      |
| -------- | ------------------------ |
| feat     | nova funcionalidade      |
| fix      | correção de bug          |
| docs     | documentação             |
| build    | mudanças de build/docker |
| refactor | refatoração              |
| perf     | melhoria de performance  |

---

# Logs do Sistema

Ver logs dos containers:

```
docker compose logs
```

Logs específicos:

```
docker compose logs api
docker compose logs worker
docker compose logs beat
```

---

# Boas Práticas

* Commits pequenos e descritivos
* Uso de branches para novas funcionalidades
* Processamento assíncrono com Celery
* Uso de Docker para padronização do ambiente

---

# Melhorias Futuras

* Dashboard de acompanhamento
* Sistema de retries nas tasks
* Monitoramento com Flower
* Métricas Prometheus
* Logs estruturados

---

# Autor

Projeto desenvolvido para automação de processamento de CDR e relatórios de campanhas.
