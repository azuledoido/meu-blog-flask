import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Rota simples para testar se o Flask está vivo
@app.route('/')
def home():
    return "<h1>O SERVIDOR ESTÁ VIVO!</h1><p>Se você está lendo isso, o erro era no Banco de Dados.</p><a href='/mural'>Tentar ir para o Mural</a>"

@app.route('/mural')
def mural():
    return render_template('mural.html', recados=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)