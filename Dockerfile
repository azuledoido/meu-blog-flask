FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ESSA LINHA É O SEGREDO PARA AS MUDANÇAS APARECEREM:
ENV FLASK_ENV=development

CMD ["python", "app.py"]