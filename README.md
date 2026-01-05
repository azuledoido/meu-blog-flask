# 🚀 Meu Blog Azul e Doido

Este é um projeto de blog pessoal desenvolvido para colocar em prática conceitos de desenvolvimento web Full Stack, integração com banco de dados e deploy em nuvem.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** [Python](https://www.python.org/)
* **Framework Web:** [Flask](https://flask.palletsprojects.com/)
* **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/) (Hospedado via Render External Database)
* **Servidor WSGI:** [Gunicorn](https://gunicorn.org/)
* **Hospedagem:** [Render](https://render.com/)
* **Controle de Versão:** Git & GitHub

## 📋 Funcionalidades

* **Feed de Notícias:** Exibição de posts com paginação por data.
* **Mural de Recados:** Espaço interativo para visitantes deixarem mensagens gravadas no banco de dados.
* **Área Administrativa:** Sistema de postagem protegido por senha para criação de novos conteúdos.
* **Arquivo Cronológico:** Organização automática de posts por ano e mês.
* **Banco de Dados na Nuvem:** Integração total entre o ambiente local (Zorin OS) e o ambiente de produção.

## 🚀 Como o projeto foi feito

O projeto foi construído seguindo a arquitetura cliente-servidor. O **Flask** gerencia as rotas e a renderização de templates HTML. A persistência de dados é feita em um banco **PostgreSQL**, garantindo que as informações não sejam perdidas entre os deploys. O deploy é feito de forma automatizada (Continuous Deployment) através da integração entre o GitHub e o **Render**.

---
*Desenvolvido por azul e doido como parte dos estudos de programação.*
