import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    try:
        url = DATABASE_URL
        if url and "sslmode" not in url:
            url += "&sslmode=require" if "?" in url else "?sslmode=require"
        return psycopg2.connect(url)
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
                EXTRACT(YEAR FROM COALESCE(data_criacao, NOW()))::int, 
                EXTRACT(MONTH FROM COALESCE(data_criacao, NOW()))::int, 
                COUNT(*)::int
            FROM posts 
            GROUP BY 1, 2 
            ORDER BY 1 DESC, 2 DESC;
        """)
        datas = cur.fetchall()
        cur.close()
        conn.close()
        return datas
    except Exception as e:
        print(f"Erro ao obter datas: {e}")
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
            # Ordenação dupla para garantir que o mais novo venha primeiro
            cur.execute("""
                SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') 
                FROM posts 
                ORDER BY data_criacao DESC, id DESC;
            """)
            posts = cur.fetchall()
            cur.close()
            conn.close()
    except:
        pass
    return render_template('index.html', posts=posts, acessos=acessos, datas_arquivo=datas_arquivo)

@app.route('/arquivo/<int:ano>/<int:mes>')
def arquivo(ano, mes):
    acessos = obter_total_acessos()
    datas_arquivo = obter_arquivo_datas()
    posts = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # Filtro por data E ordenação dupla DESC
            cur.execute("""
                SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') 
                FROM posts 
                WHERE EXTRACT(YEAR FROM data_criacao) = %s 
                AND EXTRACT(MONTH FROM data_criacao) = %s
                ORDER BY data_criacao DESC, id DESC;
            """, (ano, mes))
            posts = cur.fetchall()
            cur.close()
            conn.close()
    except:
        pass
    return render_template('index.html', posts=posts, acessos=acessos, datas_arquivo=datas_arquivo)

@app