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
        cur.execute("SELECT titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC")
        posts = cur.fetchall()
        cur.close()
        conn.close()
        lista_arquivos = obter_arquivo_datas()
        return render_template('index.html', posts=posts, datas_arquivo=lista_arquivos)
    except Exception as e:
        return f"Erro no Banco de Dados: {e}."

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == 'POST':
            nome = request.form.get('nome')
            mensagem = request.form.get('mensagem')
            if nome and mensagem:
                cur.execute('INSERT INTO mural (nome, mensagem) VALUES (%s, %s)', (nome, mensagem))
                conn.commit()
        cur.execute("SELECT nome, mensagem, TO_CHAR(data_criacao, 'DD/MM/YYYY HH24:MI') FROM mural ORDER BY data_criacao DESC")
        recados = cur.fetchall()
        lista_arquivos = obter_arquivo_datas()
        cur.close()
        conn.close()
        return render_template('mural.html', recados=recados, datas_arquivo=lista_arquivos)
    except Exception as e:
        return f"Erro no Mural: {e}"

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST':
        senha_digitada = request.form.get('senha_adm')
        if senha_digitada != SENHA_ADM:
            return "<h1>Senha Incorreta!</h1>", 403
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO posts (titulo, conteudo) VALUES (%s, %s)', (titulo, conteudo))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('escrever.html')

@app.route('/arquivo/<int:ano>/<int:mes>')
def arquivo(ano, mes):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') 
        FROM posts 
        WHERE EXTRACT(YEAR FROM data_criacao) = %s 
          AND EXTRACT(MONTH FROM data_criacao) = %s 
        ORDER BY data_criacao DESC
    """, (ano, mes))
    posts_filtrados = cur.fetchall()
    lista_arquivos = obter_arquivo_datas()
    cur.close()
    conn.close()
    return render_template('index.html', posts=posts_filtrados, datas_arquivo=lista_arquivos)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
