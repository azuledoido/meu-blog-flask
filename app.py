import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (Onde está sua DATABASE_URL)
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
            print("ERRO: DATABASE_URL não encontrada! Verifique o arquivo .env")
            return None
        if url and "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

# --- FUNÇÕES DE APOIO ---

def configurar_banco():
    """Cria as tabelas no banco de dados do Render se não existirem"""
    try:
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()
        # Tabela de Posts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Tabela do Mural
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mural (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Tabela do Contador
        cur.execute("CREATE TABLE IF NOT EXISTS contador (id SERIAL PRIMARY KEY, total INTEGER);")
        cur.execute("INSERT INTO contador (id, total) SELECT 1, 1500 WHERE NOT EXISTS (SELECT 1 FROM contador WHERE id = 1);")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Banco de dados verificado com sucesso!")
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
    except: return []

# --- ROTAS DO SITE ---

@app.route('/')
def home():
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    posts = []
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
        posts = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('index.html', posts=posts, acessos=acessos, datas_arquivo=datas_arquivo)

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    acessos = obter_total_acessos()
    if request.method == 'POST':
        nome = request.form.get('nome')
        mensagem = request.form.get('mensagem')
        if nome and mensagem:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO mural (nome, mensagem) VALUES (%s, %s)", (nome, mensagem))
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('mural'))
    
    mensagens = []
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT nome, mensagem, TO_CHAR(data_postagem, 'DD/MM HH24:MI') FROM mural ORDER BY data_postagem DESC LIMIT 30;")
        mensagens = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('mural.html', mensagens=mensagens, acessos=acessos)

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST':
        if request.form.get('senha_adm') == SENHA_ADM:
            t, c = request.form['titulo'], request.form['conteudo']
            agora_br = datetime.now(FUSO_BR)
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO posts (titulo, conteudo, data_criacao) VALUES (%s, %s, %s);', (t, c, agora_br))
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('home'))
    return render_template('escrever.html')

@app.route('/admin')
def admin():
    acessos = obter_total_acessos()
    posts = []
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
        posts = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('admin.html', posts=posts, acessos=acessos)

# --- INICIALIZAÇÃO ---

# --- INICIALIZAÇÃO ---

if __name__ == '__main__':
    configurar_banco() 
    port = int(os.environ.get("PORT", 5000))
    # O debug=True força o Flask a limpar o cache e ler os arquivos novos
    app.run(host='0.0.0.0', port=port, debug=True)