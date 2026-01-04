import os
import psycopg2
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# Senha de Administração
SENHA_ADM = "3484020200"

def get_db_connection():
    # Detecta se está no Render (DATABASE_URL) ou Local
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Correção para o driver psycopg2 aceitar a URL do Render
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgres://", 1)
        return psycopg2.connect(database_url)
    else:
        # Conexão local (Zorin OS)
        return psycopg2.connect(
            host="127.0.0.1", 
            database="meubanco", 
            user="azuledoido", 
            password="123", 
            port="5432"
        )

def obter_arquivo_datas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT 
                EXTRACT(YEAR FROM data_criacao)::int as ano,
                EXTRACT(MONTH FROM data_criacao)::int as mes,
                COUNT(*) as total
            FROM posts
            GROUP BY ano, mes
            ORDER BY ano DESC, mes DESC;
        """
        cur.execute(query)
        datas = cur.fetchall()
        cur.close()
        conn.close()
        return datas
    except:
        return []

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC")
        posts = cur.fetchall()
        cur.close()
        conn.close()
        
        lista_arquivos = obter_arquivo
