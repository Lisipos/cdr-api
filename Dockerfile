FROM python:3.11

# Definir variáveis de ambiente para não precisar interagir com o apt
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza pacotes e instala dependências básicas
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libfreetype6 \
    libgcc-s1 \
    libgdk-pixbuf-xlib-2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Adiciona a chave do Google de forma moderna
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google.gpg

# Adiciona o repositório do Google Chrome
RUN echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list

# Atualiza novamente e instala o Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
# Comando padrão (pode ser alterado conforme sua aplicação)
CMD ["google-chrome-stable", "--no-sandbox"]
# Variável para evitar warnings do Chrome no headless
ENV CHROME_BIN=/usr/bin/google-chrome


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
