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

def configurar_banco():
    conn = get_db_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, titulo TEXT NOT NULL, conteudo TEXT NOT NULL, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        cur.execute("CREATE TABLE IF NOT EXISTS mural (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, mensagem TEXT NOT NULL, data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        cur.execute("CREATE TABLE IF NOT EXISTS contador (id SERIAL PRIMARY KEY, total INTEGER);")
        cur.execute("INSERT INTO contador (id, total) SELECT 1, 1500 WHERE NOT EXISTS (SELECT 1 FROM contador WHERE id = 1);")
        conn.commit()
        cur.close()
        conn.close()
    except: pass

def obter_total_acessos():
    try:
        conn = get_db_connection()
        if not conn: return "1500+"
        cur = conn.cursor()
        cur.execute("UPDATE contador SET total = total + 1 WHERE id = 1 RETURNING total")
        total = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return total
    except: return "1500+"

@app.route('/')
def home():
    posts, acessos = [], obter_total_acessos()
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
            posts = cur.fetchall()
            cur.close()
            conn.close()
    except: pass
    return render_template('index.html', posts=posts, acessos=acessos)

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    if request.method == 'POST':
        n, m = request.form.get('nome'), request.form.get('mensagem')
        if n and m:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor(); cur.execute("INSERT INTO mural (nome, mensagem) VALUES (%s, %s)", (n, m))
                conn.commit(); cur.close(); conn.close()
                return redirect(url_for('mural'))
    mensagens = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT nome, mensagem, TO_CHAR(data_postagem, 'DD/MM HH24:MI') FROM mural ORDER BY data_postagem DESC LIMIT 30;")
            mensagens = cur.fetchall()
            cur.close(); conn.close()
    except: pass
    return render_template('mural.html', mensagens=mensagens, acessos=obter_total_acessos())

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST' and request.form.get('senha_adm') == SENHA_ADM:
        t, c = request.form.get('titulo'), request.form.get('conteudo')
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO posts (titulo, conteudo, data_criacao) VALUES (%s, %s, %s);', (t, c, datetime.now(FUSO_BR)))
            conn.commit(); cur.close(); conn.close()
            return redirect(url_for('home'))
    return render_template('escrever.html')

configurar_banco()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)