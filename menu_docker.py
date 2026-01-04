import os

def limpar_tela():
    os.system('clear')

def menu():
    # Centralizando a pasta do projeto
    pasta = "/home/azul/estudos_docker"
    
    while True:
        limpar_tela()
        print("--- 🔵 SISTEMA MURAL AZULEDOIDO 2026 🔵 ---")
        print("1. Ver Status (Containers Online)")
        print("2. LIGAR SISTEMA (App + Banco)")
        print("3. VER LOGS (Acompanhar em tempo real)")
        print("4. VER RECADOS (Direto no Postgres)")
        print("5. RESET DE FÁBRICA (Limpar tudo e apagar dados)")
        print("6. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            print("\n--- CONTAINERS ATIVOS ---")
            os.system("docker ps")
            input("\nEnter para voltar.")
        
        elif opcao == '2':
            print("\n🚀 Subindo Orquestração (Buildando novidades)...")
            # Usamos o --build para garantir que as mudanças no app_azuledoido.py entrem no Docker
            os.system(f"cd {pasta} && docker compose up -d --build")
            print("\n✅ Sistema ON! Acesse: http://localhost:5000")
            input("\nEnter para voltar.")
        
        elif opcao == '3':
            print("\n👀 Mostrando Logs (Pressione CTRL+C para sair dos logs e voltar ao menu)")
            # Mostra logs do app e do banco juntos para você ver a conversa entre eles
            os.system(f"cd {pasta} && docker compose logs -f")
            input("\nVoltando ao menu... Enter.")

        elif opcao == '4':
            print("\n--- 📝 RECADOS NO BANCO DE DADOS ---")
            os.system(f"docker exec -it estudos_docker_pgdb_1 psql -U azuledoido -d meubanco -c 'SELECT * FROM mensagens;'")
            input("\nEnter para voltar.")

        elif opcao == '5':
            confirmar = input("\n⚠️ Isso vai apagar TODOS os recados e resetar o banco. Confirma? (s/n): ")
            if confirmar.lower() == 's':
                print("\n🧹 Limpando volumes e containers...")
                os.system(f"cd {pasta} && docker compose down -v")
                os.system(f"sudo rm -rf /home/azul/postgres_data_segura/*")
                input("\nReset concluído! Use a opção 2 para ligar novamente. Enter.")
        
        elif opcao == '6':
            print("Até logo, azul e doido! Salvando progresso...")
            break
        
        else:
            input("Opção inválida! Aperte Enter.")

if __name__ == "__main__":
    menu()
