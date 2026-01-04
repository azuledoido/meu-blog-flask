import xml.etree.ElementTree as ET
import psycopg2
import re

def limpar_html_sujo(texto):
    if not texto: return ""
    # Remove tags de estilo e scripts que o WordPress as vezes injeta
    texto = re.sub(r'<style.*?>.*?</style>', '', texto, flags=re.DOTALL)
    texto = re.sub(r'<script.*?>.*?</script>', '', texto, flags=re.DOTALL)
    # Converte quebras de linha do WP em <br> para o seu site entender
    texto = texto.replace('\n', '<br>')
    return texto

def importar_v2():
    try:
        conn = psycopg2.connect(
            host="localhost", port="5432",
            database="meubanco", user="azuledoido", password="123"
        )
        cur = conn.cursor()
        
        # Limpa o que sobrou antes de começar
        cur.execute("TRUNCATE TABLE posts;")
        
        tree = ET.parse('meu_blog.xml')
        root = tree.getroot()
        
        count = 0
        # O WordPress usa esse padrão de busca para os itens
        for item in root.findall('.//item'):
            titulo = item.find('title').text
            
            # Tenta pegar o conteúdo codificado (padrão WP)
            conteudo_raw = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            if conteudo_raw is None:
                conteudo_raw = item.find('description') # Backup caso não ache o principal
            
            if titulo and conteudo_raw is not None:
                texto_limpo = limpar_html_sujo(conteudo_raw.text)
                
                cur.execute(
                    "INSERT INTO posts (titulo, conteudo) VALUES (%s, %s)",
                    (titulo, texto_limpo)
                )
                count += 1
        
        conn.commit()
        print(f"🚀 SUCESSO! {count} posts limpos e importados.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    importar_v2()
