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
cloudinary.config(
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# --- CORREÇÃO DE ERRO 403 E PERMISSÕES ---
@app.after_request
def add_header(response):
    # Libera o acesso para bots de redes sociais (CORS)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    # Garante que o cache não trave versões antigas durante os testes
    if request.path.startswith('/post/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/robots.txt')
def robots():
    # Resposta limpa e direta para os bots
    return Response("User-agent: *\nAllow: /", mimetype="text/plain")

# --- FUNÇÕES DE BANCO ---
def get_db_connection():
    try:
        url = DATABASE_URL
        if not url: return None
        if "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        return psycopg2.connect(url)
    except: return None

def extrair_primeira_img(conteudo):
    if not conteudo: return None
    match = re.search(r'<img [^>]*src="([^"]+)"', conteudo)
    return match.group(1) if match else None

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
        cur.execute("SELECT EXTRACT(YEAR FROM data_criacao)::int, EXTRACT(MONTH FROM data_criacao)::int, COUNT(*)::int FROM posts GROUP BY 1, 2 ORDER BY 1 DESC, 2 DESC;")
        d = cur.fetchall(); cur.close(); conn.close()
        return d
    except: return []

# --- ROTAS DE ADMINISTRAÇÃO E UPLOAD ---
@app.route('/upload_cloudinary', methods=['POST'])
def upload_cloudinary():
    if request.form.get('senha') != SENHA_ADM:
        return "Senha incorreta", 403
    if 'foto' not in request.files:
        return "Nenhum arquivo enviado", 400
    arquivo = request.files['foto']
    if arquivo.filename == '':
        return "Arquivo sem nome", 400
    try:
        resultado = cloudinary.uploader.upload(arquivo)
        link_direto = resultado['secure_url']
        return f"Link Gerado com Sucesso! Copie e use no post:<br><br><b>{link_direto}</b><br><br><a href='javascript:history.back()'>Voltar</a>"
    except Exception as e:
        return f"Erro no upload: {str