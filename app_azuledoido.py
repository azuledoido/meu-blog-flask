import os
import psycopg2
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# Senha de Administração
SENHA_ADM = "3484020200"

def get_db_connection():
    # Tenta obter a URL do Render
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Correção automática: o Render às vezes manda 'postgresql://', 
        # mas o driver psycopg2 prefere 'postgres://'
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgres://", 1)
        
        # Conexão para o Render (Nuvem)
        return psycopg2.connect(database_url)
    else:
        # Conexão clássica local (Zorin)
        return psycopg2.connect(
            host="127.0.
