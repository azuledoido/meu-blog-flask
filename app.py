import os, psycopg2, pytz, re
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, abort, Response
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False

# CONFIGURAÇÕES
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')
FUSO_BR = pytz.timezone('America/Sao_Paulo')

# CONFIGURAÇÃO CLOUDINARY
try:
    cloudinary.config(
      cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
      api_key = os.environ.get('CLOUDINARY_API_KEY'), 
      api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    )
except Exception as e:
    print(f"Erro ao configurar Cloudinary: {e}")

# --- CABEÇALHOS ANTI-BLOQUEIO (403) ---
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.path.startswith('/post/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# ROTA ROBOTS CORRIGIDA (EVITA 404)
@app.route('/robots.txt')
@app.route('/robots.txt/')
def robots():
    return Response("User-agent: *\nAllow: /", mimetype="text/plain")

def get_db_connection():
    try:
        url = DATABASE_URL
        if not url: return None
        if "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        return psycopg2.connect(url)
    except Exception as e:
        print(f"Erro de conexão com DB: {e}")
        return None

def extrair_primeira_img(conteudo):
    if not conteudo: return None
    match = re.search(r'<img [^>]*src="([^"]+)"', conteudo)
    return match.group(1) if match else None

def obter_total_acessos():
    try:
        conn = get_db_connection()
        if not conn: return "1500+"
        cur = conn.cursor()
        cur.execute("UPDATE contador SET total = total + 1 WHERE id = 1 RETURNING total")
        t = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()
        return t
    except: return "1500+"

def obter_arquivo_datas():
    try:
        conn = get_db_connection()
        if not conn: return []
        cur = conn.cursor()
        cur.execute("SELECT EXTRACT(YEAR FROM data_criacao)::int, EXTRACT(MONTH FROM data_criacao)::int, COUNT(*)::int FROM posts GROUP BY 1, 2 ORDER BY 1 DESC, 2 DESC;")
        d = cur.fetchall(); cur.close(); conn.close()
        return d
    except: return []

@app.route('/upload_cloudinary', methods=['POST'])
def upload_cloudinary():
    if request.form.get('senha') != SENHA_ADM: return "Senha incorreta", 403
    arquivo = request.files.get('foto')
    if not arquivo or arquivo.filename == '': return "Arquivo inválido", 400
    try:
        resultado = cloudinary.uploader.upload(arquivo)
        return f"Link: <b>{resultado['secure_url']}</b><br><br><a href='javascript:history.back()'>Voltar</a>"
    except Exception as e: return f"Erro: {str(e)}"

@app.route('/')
def home():
    acessos = obter_total_acessos()
    datas = obter_arquivo_datas()
    try:
        conn = get_db_connection()
        if not conn: return render_template('index.html', posts=[], acessos=acessos, datas_arquivo=datas)
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
        p_brutos = cur.fetchall(); cur.close(); conn.close()
        posts_com_img = [list(p) + [extrair_primeira_img(p[2])] for