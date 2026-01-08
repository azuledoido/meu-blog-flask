import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configurações
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')
FUSO_BR = pytz.timezone('America/Sao_Paulo')

def get_db_connection():
    try:
        url = DATABASE_URL
        if not url:
            return None
        if "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

# --- FUNÇÕES DE APOIO ---

def configurar_banco():
    conn = get_db_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS mural (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contador (id SERIAL PRIMARY KEY, total INTEGER);
        """)
        cur.execute("INSERT INTO contador (id, total) SELECT 1, 1500 WHERE NOT EXISTS (SELECT 1 FROM contador WHERE id = 1);")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao configurar banco: {e}")

def obter_total_acessos():
    try:
        conn = get_db_connection()
        if not conn: return "1500+"
        cur = conn.cursor()
        cur.execute("UPDATE contador SET total = total + 1 WHERE id = 1")
        conn.commit()
        cur.execute("SELECT total FROM contador WHERE id = 1")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return total
    except:
        return "1500+"

def obter_arquivo_datas():
    try:
        conn = get_db_connection()
        if not conn: return []
        cur = conn.cursor()
        cur.execute("""
            SELECT EXTRACT(YEAR FROM data_criacao)::int, EXTRACT(MONTH FROM data_criacao)::int, COUNT(*)::int
            FROM posts GROUP BY 1, 2 ORDER BY 1 DESC, 2 DESC;
        """)
        datas = cur.fetchall()
        cur.close()
        conn.close()
        return datas
    except:
        return []

# --- ROTAS DO SITE ---

@app.route('/')
def home():
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    posts = []
    try:
        conn = get_db_connection()
        if