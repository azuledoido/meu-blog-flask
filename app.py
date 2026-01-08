import os, psycopg2, pytz
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False

SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')
FUSO_BR = pytz.timezone('America/Sao_Paulo')

def get_db_connection():
    try:
        url = DATABASE_URL
        if not url: return None
        if "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        return psycopg2.connect(url)
    except: return None

def obter_total_acessos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE contador SET total = total + 1 WHERE id = 1 RETURNING total")
        t = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()
        return t
    except: return "1500+"

def obter_arquivo_datas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT EXTRACT(YEAR FROM data_criacao)::int as ano, 
                   EXTRACT(MONTH FROM data_criacao)::int as mes, 
                   COUNT(*)::int 
            FROM posts GROUP BY 1, 2 ORDER BY 1 DESC, 2 DESC;
        """)
        d = cur.fetchall(); cur.close(); conn.close()
        return d
    except: return []

@app.route('/')
def home():
    acessos = obter_total_acessos()
    datas = obter_arquivo_datas()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
        p = cur.fetchall(); cur.close(); conn.close()
        return render_template('index.html', posts=p, acessos=acessos, datas_arquivo=datas)
    except: return render_template('index.html', posts=[], acessos=acessos, datas_arquivo=datas)

# --- NOVA ROTA INTEGRADA PARA DESCONGELAR O ARQUIVO ---
@app.route('/arquivo/<int:ano>/<int:mes>')
def arquivo_data(ano, mes):
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY