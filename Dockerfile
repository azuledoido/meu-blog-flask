FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# Esta linha abaixo é que garante que o código E a pasta templates entram no Docker
COPY . . 
CMD ["python", "app_azuledoido.py"]
