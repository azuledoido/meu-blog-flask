import os, psycopg2, pytz, re
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, abort, Response
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False

# --- FILTRO PARA O HTML FUNCIONAR ---
@app.template_filter('select_img')
def select_img_filter(content):
    return extrair_primeira_img(content)

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

# ROTA ROBOTS (ESSENCIAL PARA O THREADS)
@app.route('/robots.txt')
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
    # Busca a URL da primeira imagem no HTML do post
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
        posts_com_img = [list(p) + [extrair_primeira_img(p[2])] for p in p_brutos]
        return render_template('index.html', posts=posts_com_img, acessos=acessos, datas_arquivo=datas)
    except: return render_template('index.html', posts=[], acessos=acessos, datas_arquivo=datas)

@app.route('/post/<int:post_id>')
def exibir_post(post_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY HH24:MI') FROM posts WHERE id = %s", (post_id,))
        p = cur.fetchone(); cur.close(); conn.close()
        if p: return render_template('post.html', post=p, acessos=obter_total_acessos())
        return redirect(url_for('home'))
    except: return redirect(url_for('home'))

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST' and request.form.get('senha_adm') == SENHA_ADM:
        t, c = request.form.get('titulo'), request.form.get('conteudo')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO posts (titulo, conteudo, data_criacao) VALUES (%s, %s, %s);', (t, c, datetime.now(FUSO_BR)))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('home'))
    return render_template('escrever.html')

@app.route('/editar/<int:post_id>', methods=['GET', 'POST'])
def editar_post(post_id):
    senha = request.args.get('senha') or request.form.get('senha_adm')
    if senha != SENHA_ADM: return "Acesso negado", 403
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        t, c = request.form.get('titulo'), request.form.get('conteudo')
        cur.execute('UPDATE posts SET titulo = %s, conteudo = %s WHERE id = %s', (t, c, post_id))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('admin_posts', senha_sucesso=SENHA_ADM))
    cur.execute("SELECT id, titulo, conteudo FROM posts WHERE id = %s", (post_id,))
    p = cur.fetchone(); cur.close(); conn.close()
    return render_template('editar.html', post=p, senha=senha) if p else redirect(url_for('admin_posts'))

@app.route('/admin_posts', methods=['GET', 'POST'])
def admin_posts():
    senha = request.form.get('senha') or request.args.get('senha_sucesso')
    if senha == SENHA_ADM:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, TO_CHAR(data_criacao, 'DD/MM/YY HH24:MI') FROM posts ORDER BY data_criacao DESC")
        posts = cur.fetchall(); cur.close(); conn.close()
        return render_template('admin_posts.html', posts=posts, senha=SENHA_ADM)
    return render_template('admin_posts.html', posts=[])

@app.route('/deletar/<int:post_id>', methods=['POST'])
def deletar_post(post_id):
    if request.form.get('senha') == SENHA_ADM:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit(); cur.close(); conn.close()
    return redirect(url_for('admin_posts'))

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    if request.method == 'POST':
        n, m = request.form.get('nome'), request.form.get('mensagem')
        if n and m:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO mural (nome, mensagem) VALUES (%s, %s)", (n, m))
            conn.commit(); cur.close(); conn.close()
            return redirect(url_for('mural'))
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome, mensagem, TO_CHAR(data_postagem, 'DD/MM HH24:MI') FROM mural ORDER BY data_postagem DESC LIMIT 30;")
        msg = cur.fetchall(); cur.close(); conn.close()
        return render_template('mural.html', mensagens=msg, acessos=obter_total_acessos())
    except: return render_template('mural.html', mensagens=[], acessos="1500+")

@app.route('/arquivo/<int:ano>/<int:mes>')
def arquivo_data(ano, mes):
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts WHERE EXTRACT(YEAR FROM data_criacao) = %s AND EXTRACT(MONTH FROM data_criacao) = %s ORDER BY data_criacao DESC;", (ano, mes))
        p_brutos = cur.fetchall(); cur.close(); conn.close()
        posts_com_img = [list(p) + [extrair_primeira_img(p[2])] for p in p_brutos]
        return render_template('index.html', posts=posts_com_img, acessos=acessos, datas_arquivo=datas_arquivo)
    except: return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)