# Usar uma imagem base do Python
FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos do projeto para o diretório de trabalho
COPY . /app

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências do projeto
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Expor a porta que será usada pelo FastAPI
EXPOSE 8000

# Comando para rodar o servidor
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

