import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pytz

app = Flask(__name__)

# Configurações
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')
FUSO_BR = pytz.timezone('America/Sao_Paulo')

def get_db_connection():
    try:
        url = DATABASE_URL
        if url and "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def obter_total_acessos():
    try:
        conn = get_db_connection()
        if not conn: return "1500+"
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS contador (id SERIAL PRIMARY KEY, total INTEGER);")
        cur.execute("INSERT INTO contador (id, total) SELECT 1, 1500 WHERE NOT EXISTS (SELECT 1 FROM contador WHERE id = 1);")
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
            SELECT 
                EXTRACT(YEAR FROM data_criacao)::int, 
                EXTRACT(MONTH FROM data_criacao)::int, 
                COUNT(*)::int
            FROM posts 
            GROUP BY 1, 2 
            ORDER BY 1 DESC, 2 DESC;
        """)
        datas = cur.fetchall()
        cur.close()
        conn.close()
        return datas
    except:
        return []

@app.route('/')
def home():
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    posts = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
            posts = cur.fetchall()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Erro home: {e}")
    return render_template('index.html', posts=posts, acessos=acessos, datas_arquivo=datas_arquivo)

# AQUI: Rota configurada para o arquivo admin.html
@app.route('/admin')
def admin():
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    posts = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # Seleciona exatamente o que o seu HTML pede: ID, Título e Data
            cur.execute("SELECT id, titulo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC;")
            posts = cur.fetchall()
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Erro admin: {e}")
    
    # IMPORTANTE: O nome aqui deve ser admin.html
    return render_template('admin.html', posts=posts, acessos=acessos, datas_arquivo=datas_arquivo)

@app.route('/deletar/<int:post_id>', methods=['POST'])
def deletar_post(post_id):
    senha = request.form.get('senha_adm')
    if senha == SENHA_ADM:
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                conn.commit()
                cur.close()
                conn.close()
        except:
            pass
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)