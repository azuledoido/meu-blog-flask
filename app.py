import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # Se não houver DATABASE_URL (local), usa o padrão de teste
    url = DATABASE_URL if DATABASE_URL else 'postgresql://azuledoido:123@localhost:5432/meubanco'
    return psycopg2.connect(url)

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
    except Exception as e:
        print(f"Erro nas datas: {e}")
        return []

@app.route('/')
def home():
    try:
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
    except Exception as e:
        return f"Erro crítico na Home: {e}"

@app.route('/mural', methods=['GET', 'POST'])
def mural():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == 'POST':
            nome = request.form.get('nome')
            mensagem = request.form.get('mensagem')
            if nome and mensagem:
                cur.execute("INSERT INTO mural (nome, mensagem) VALUES (%s, %s)", (nome, mensagem))
                conn.commit()
            return redirect(url_for('mural'))

        cur.execute("SELECT id, nome, mensagem, TO_CHAR(data, 'DD/MM/YYYY HH24:MI') FROM mural ORDER BY id DESC LIMIT 50")
        recados = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('mural.html', recados=recados)
    except Exception as e:
        return f"Erro no Mural: {e}"

@app.route('/post/<int:post_id>')
def exibir_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts WHERE id = %s;", (post_id,))
    post = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('post_unico.html', post=post)

@app.route('/escrever', methods=['GET', 'POST'])
def escrever():
    if request.method == 'POST':
        if request.form.get('senha_adm') == SENHA_ADM:
            t, c = request.form['titulo'], request.form['conteudo']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO posts (titulo, conteudo) VALUES (%s, %s);', (t, c))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('home'))
    return render_template('escrever.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)