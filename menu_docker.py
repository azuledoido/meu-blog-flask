import os
from datetime import datetime

def limpar_tela():
    os.system('clear')

def menu():
    # Caminho da sua pasta
    pasta = "/home/azul/estudos_docker"
    # Nome do container do banco conforme identificado pelo seu sistema
    container_db = "estudos_docker-db-1"
    
    while True:
        limpar_tela()
        print("--- 🔵 PAINEL DE CONTROLE: AZULEDOIDO 2026 🔵 ---")
        print("1. Ver Status (Containers Online)")
        print("2. LIGAR BANCO (Docker Up)")
        print("3. LIMPAR AMBIENTE (Docker Down - Parar tudo)")
        print("4. 🚀 INICIAR BLOG (Rodar app_azuledoido.py)")
        print("5. 💾 FAZER BACKUP (Gerar arquivo .sql)")
        print("6. VER RECADOS (Direto no Postgres)")
        print("7. RESET DE FÁBRICA (Cuidado!)")
        print("8. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            print("\n--- CONTAINERS ATIVOS ---")
            os.system("docker ps")
            input("\nEnter para voltar.")
        
        elif opcao == '2':
            print("\n🚀 Subindo containers...")
            os.system(f"cd {pasta} && docker compose up -d")
            input("\n✅ Banco Online! Enter para voltar.")

        elif opcao == '3':
            print("\n🧹 Limpando e parando tudo...")
            os.system(f"cd {pasta} && docker compose down")
            input("\n✅ Sistema desligado com sucesso. Enter para voltar.")

        elif opcao == '4':
            print("\n🌐 Iniciando o Blog Flask... (CTRL+C para encerrar)")
            os.system(f"cd {pasta} && python3 app_azuledoido.py")
        
        elif opcao == '5':
            data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M")
            nome_arquivo = f"backup_blog_{data_atual}.sql"
            print(f"\n📦 Criando backup: {nome_arquivo}")
            # COMANDO CORRIGIDO COM O NOME DO CONTAINER ATUAL
            os.system(f"docker exec {container_db} pg_dump -U azuledoido meubanco > {pasta}/{nome_arquivo}")
            print(f"\n✅ Salvo na pasta {pasta}!")
            input("\nEnter para voltar.")

        elif opcao == '6':
            print("\n--- 📝 RECADOS NO BANCO ---")
            # COMANDO CORRIGIDO PARA VER MENSAGENS
            os.system(f"docker exec -it {container_db} psql -U azuledoido -d meubanco -c 'SELECT * FROM mensagens;'")
            input("\nEnter para voltar.")

        elif opcao == '7':
            confirmar = input("\n⚠️ APAGAR TUDO (Inclusive mensagens)? (s/n): ")
            if confirmar.lower() == 's':
                os.system(f"cd {pasta} && docker compose down -v")
                print("\nReset concluído.")
                input("\nEnter.")
        
        elif opcao == '8':
            print("Até logo, azul e doido!")
            break
        
        else:
            input("Opção inválida! Aperte Enter.")

if __name__ == "__main__":
    menu()
