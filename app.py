@app.route('/mural', methods=['GET', 'POST'])
def mural():
    recados = [] # Começa vazio para não dar erro no HTML
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

        # Tentativa de busca: se a coluna 'data' não existir, o except captura
        cur.execute("SELECT id, nome, mensagem FROM mural ORDER BY id DESC LIMIT 50")
        recados = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco do mural: {e}")
        # Aqui ele não dá 'return', ele segue para renderizar o template mesmo vazio
    
    return render_template('mural.html', recados=recados)