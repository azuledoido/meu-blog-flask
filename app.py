import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

# 1. ISSO PRECISA VIR PRIMEIRO
app = Flask(__name__)

SENHA_ADM = "3484020200"
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    url = DATABASE_URL if DATABASE_URL else 'postgresql://azuledoido:123@localhost:5432/meubanco'
    return psycopg2.connect(url)

# 2. AGORA AS ROTAS PODEM USAR O 'app'
@app.route('/mural', methods=['GET', 'POST'])
def mural():
    recados = []
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

        cur.execute("SELECT id, nome, mensagem FROM mural ORDER BY id DESC LIMIT 50")
        recados = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")
    
    return render_template('mural.html', recados=recados)

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, conteudo, TO_CHAR(data_criacao, 'DD/MM/YYYY') FROM posts ORDER BY id DESC;")
        posts = cur.fetchall()
        cur.close()
        conn.close()
        # Nota: removi o contador e arquivo temporariamente para garantir que o site suba
        return render_template('index.html', posts=posts, acessos="Calculando...")
    except Exception as e:
        return f"Erro na Home: {e}"

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