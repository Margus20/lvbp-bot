import requests
from bs4 import BeautifulSoup
import os
import datetime

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
LOGO = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

# RSS de Google News para Tiburones de La Guaira
RSS_URL = "https://news.google.com/rss/search?q=%22Tiburones+de+La+Guaira%22&hl=es&gl=VE&ceid=VE:es"

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    img_data = requests.get(url_img, timeout=10).content
    files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
    data = {
        'chat_id': CHANNEL,
        'caption': texto,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    r = requests.post(url, files=files, data=data, timeout=20)
    print("Status foto: " + str(r.status_code))

def obtener_noticias_google():
    print("Obteniendo noticias de Google News...")
    noticias = []
    
    try:
        response = requests.get(RSS_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('item')
        
        for item in items[:5]:  # Máximo 5 noticias
            titulo_tag = item.find('title')
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
            
            descripcion_tag = item.find('description')
            descripcion = descripcion_tag.get_text(strip=True) if descripcion_tag else ""
            
            if titulo and len(titulo) > 10:
                noticias.append({
                    'titulo': titulo,
                    'descripcion': descripcion[:200]
                })
        
        print("Noticias encontradas: " + str(len(noticias)))
        
    except Exception as e:
        print("Error obteniendo RSS: " + str(e))
    
    return noticias

def main():
    print("Iniciando bot...")
    
    # 1. Obtener noticias de Google News
    noticias = obtener_noticias_google()
    
    # 2. Publicar cada noticia con el logo
    for i, noticia in enumerate(noticias[:3]):
        titulo = noticia['titulo']
        descripcion = noticia['descripcion']
        
        texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>"
        if descripcion:
            texto += "\n\n" + descripcion
        
        enviar_foto(LOGO, texto)
        print("Publicada noticia " + str(i+1))
    
    # 3. Publicar Calendario
    link_cal = "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
    texto_cal = "📅 <b>CALENDARIO TIBURONES - OCTUBRE 2026</b>\n\nSemana 1: 12-16 de octubre"
    enviar_foto(link_cal, texto_cal)
    
    print("Proceso terminado.")

if __name__ == '__main__':
    main()
