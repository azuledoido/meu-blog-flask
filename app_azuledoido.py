import os
import psycopg2
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# Senha de Administração
SENHA_ADM = "3484020200"

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgres://", 1)
        return psycopg2.connect(database_url)
    else:
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
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC")
        posts = cur.fetchall()
        cur.close()
        conn.close()
        lista_arquivos = obter_arquivo_datas()
        return render_template('index.html', posts=posts, datas_arquivo=lista_arquivos)
    except Exception as e:
        return f"Erro no Banco de Dados: {e}."

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def exibir_post(post_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == 'POST':
            nome = request.form.get('nome')
            comentario = request.form.get('comentario')
            if nome and comentario:
                cur.execute('INSERT INTO comentarios_posts (post_id, nome, comentario) VALUES (%s, %s, %s)', (post_id, nome, comentario))
                conn.commit()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        cur.execute("SELECT nome, comentario, TO_CHAR(data_criacao, 'DD/MM/YYYY HH24:MI') FROM comentarios_posts WHERE post_id = %s ORDER BY data_criacao DESC", (post_id,))
        comentarios = cur.fetchall()
        cur.close()
        conn.close()
        if post:
            lista_arquivos = obter_arquivo_datas()
            return render_template('post_unico.html', post=post, comentarios=comentarios, datas_arquivo=lista_arquivos)
        else:
            return "Post não encontrado", 404
    except Exception as e:
        return f"Erro ao carregar o post: {e}"

# --- NOVAS ROTAS DE GERENCIAMENTO ---

@app.route('/admin/comentarios')
def admin_comentarios():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # JOIN para saber o título do post onde o comentário foi feito
        cur.execute("""
            SELECT c.id, c.nome, c.comentario, TO_CHAR(c.data_criacao, 'DD/MM HH24:MI'), p.titulo 
            FROM comentarios_posts c
            JOIN posts p ON c.post_id = p.id
            ORDER BY c.data_criacao DESC
        """)
        comentarios = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('admin_comentarios.html', comentarios=comentarios)
    except Exception as e:
        return f"Erro na moderação: {e}"

@app.route('/deletar_comentario/<int:com_id>', methods=['POST'])
def deletar_comentario(com_id):
    senha = request.form.get('senha_adm')
    if senha == SENHA_ADM:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM comentarios_posts WHERE id = %s", (com_id,))
