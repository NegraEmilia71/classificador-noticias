FROM python:3.9-slim

# Configuração do ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Download dos modelos do spaCy para português
RUN python -m spacy download pt_core_news_sm

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/raw data/processed models

# Expor porta da API
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
