FROM python:3.9-slim

# Copiar o conteúdo do projeto para dentro da imagem
COPY . /app

WORKDIR /app

# Instalar as dependências
RUN pip install -r requirements.txt

# Expor a porta 5000
EXPOSE 5000

# Iniciar a aplicação
CMD ["python", "app.py"]
