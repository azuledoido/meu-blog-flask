import os
import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
SENHA_ADM = "3484020200"

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL', 'postgresql://azuledoido:123@pgdb:5432/meubanco')
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
        cur.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, titulo TEXT, conteudo TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
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
        cur.execute("CREATE TABLE IF NOT EXISTS mural (id SERIAL PRIMARY KEY, nome TEXT, mensagem TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        if request.method == 'POST':
            n = request.form.get('nome')
            m = request.form.get('recado') 
            if n and m:
                cur.execute('INSERT INTO mural (nome, mensagem) VALUES (%s, %s)', (n, m))
                conn.commit()
        cur.execute("SELECT nome, mensagem, TO_CHAR(data_criacao, 'HH24:MI - DD/MM') FROM mural ORDER BY data_criacao DESC")
        recados = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('mural.html', recados=recados)
    except Exception as e:
        return f"Erro no Mural: {e}"

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def exibir_post(post_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS comentarios_posts (id SERIAL PRIMARY KEY, post_id INTEGER, nome TEXT, comentario TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        if request.method == 'POST':
            nome = request.form.get('nome')
            comentario = request.form.get('comentario')
            if nome and comentario:
                cur.execute('INSERT INTO comentarios_posts (post_id, nome, comentario) VALUES (%s, %s, %s)', (post_id, nome, comentario))
                conn.commit()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        cur.execute("SELECT nome, comentario, TO_CHAR(data_criacao, 'DD/MM HH24:MI') FROM comentarios_posts WHERE post_id = %s ORDER BY data_criacao DESC", (post_id,))
        comentarios = cur.fetchall()
        datas = obter_arquivo_datas()
        cur.close()
        conn.close()
        return render_template('post_unico.html', post=post, comentarios=comentarios, datas_arquivo=datas)
    except Exception as e:
        return f"Erro no Post: {e}"

@app.route('/arquivo/<int:ano>/<int:mes>')
def arquivo(ano, mes):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') 
            FROM posts 
            WHERE EXTRACT(YEAR FROM data_criacao) = %s 
            AND EXTRACT(MONTH FROM data_criacao) = %s 
            ORDER BY data_criacao DESC
        """, (ano, mes))
        posts = cur.fetchall()
        datas = obter_arquivo_datas()
        cur.close()
        conn.close()
        return render_template('index.html', posts=posts, datas_arquivo=datas)
    except Exception as e:
        return f"Erro no Arquivo: {e}"

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST':
        if request.form.get('senha_adm') == SENHA_ADM:
            t, c = request.form['titulo'], request.form['conteudo']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO posts (titulo, conteudo) VALUES (%s, %s)', (t, c))
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/')
    return render_template('escrever.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
