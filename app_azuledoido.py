import os
import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
SENHA_ADM = "3484020200"

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgres://", 1)
    return psycopg2.connect(database_url)

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
    except Exception as e:
        print(f"Erro no contador: {e}")
        return "---"

def obter_arquivo_datas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT EXTRACT(YEAR FROM data_criacao)::int, 
                   EXTRACT(MONTH FROM data_criacao)::int, 
                   COUNT(*) 
            FROM posts 
            GROUP BY 1, 2 
            ORDER BY 1 DESC, 2 DESC
        """)
        datas = cur.fetchall()
        cur.close()
        conn.close()
        return datas
    except:
        return []

@app.route('/')
def home():
    try:
        acessos = obter_total_acessos()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY data_criacao DESC")
        posts = cur.fetchall()
        datas = obter_arquivo_datas()
        cur.close()
        conn.close()
        return render_template('index.html', posts=posts, datas_arquivo=datas, acessos=acessos)
    except Exception as e:
        return f"Erro na Home: {e}"

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == 'POST':
            n = request.form.get('nome')
            m = request.form.get('recado') 
            if n and m:
                cur.execute('INSERT INTO mural (nome, mensagem) VALUES (%s, %s)', (n, m))
                conn.commit()
        cur.execute("SELECT nome, mensagem, TO_CHAR(data_criacao, 'HH24:
