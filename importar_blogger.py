import xml.etree.ElementTree as ET
import psycopg2

def importar_tudo_blogger():
    # Namespaces comuns em arquivos Atom do Blogger
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    try:
        conn = psycopg2.connect(
            host="localhost", port="5432",
            database="meubanco", user="azuledoido", password="123"
        )
        cur = conn.cursor()
        
        tree = ET.parse('blog_blogger.xml')
        root = tree.getroot()
        
        # Procura todas as 'entry' no arquivo
        entries = root.findall('atom:entry', ns)
        print(f"🔎 Encontrei {len(entries)} entradas no arquivo. Processando...")
        
        count = 0
        for entry in entries:
            titulo_elem = entry.find('atom:title', ns)
            conteudo_elem = entry.find('atom:content', ns)
            
            # Pegamos o texto se ele existir
            titulo = titulo_elem.text if titulo_elem is not None and titulo_elem.text else "Sem título"
            conteudo = conteudo_elem.text if conteudo_elem is not None and conteudo_elem.text else ""

            # Só importa se tiver conteúdo (evita importar tags vazias de configuração)
            if conteudo and len(conteudo) > 50: 
                cur.execute(
                    "INSERT INTO posts (titulo, conteudo) VALUES (%s, %s)",
                    (titulo, conteudo)
                )
                count += 1
        
        conn.commit()
        print(f"✅ SUCESSO! {count} itens do Blogger foram salvos no banco.")

    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    importar_tudo_blogger()
