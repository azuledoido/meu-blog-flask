import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://azuledoido:123@pgdb:5432/meubanco')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def obter_total_acessos():
    try:
        conn = get_db_connection()
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
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                EXTRACT(YEAR FROM COALESCE(data_criacao, NOW()))::int, 
                EXTRACT(MONTH FROM COALESCE(data_criacao, NOW()))::int, 
                COUNT(*) 
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') 
        FROM posts 
        ORDER BY data_criacao DESC, id DESC;
    """)
    posts = cur.fetchall()
    datas = obter_arquivo_datas()
    cur.close()
    conn.close()
    return render_template('index.html', posts=posts, datas_arquivo=datas, acessos=acessos)

# --- ROTA DO MURAL ADICIONADA AQUI ---
@app.route('/mural', methods=['GET', 'POST'])
def mural():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        mensagem = request.form.get('mensagem')
        if nome and mensagem:
            cur.execute("INSERT INTO mural (nome, mensagem) VALUES (%s, %s)", (nome, mensagem))
            conn.commit()
        return redirect(url_for('mural'))

    try:
        cur.execute("SELECT id, nome, mensagem, TO_CHAR(data, 'DD/MM/YYYY HH24:MI') FROM mural ORDER BY id DESC")
        recados = cur.fetchall()
    except:
        recados = []