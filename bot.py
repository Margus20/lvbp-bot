import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
LOGO = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"
RSS_URL = "https://news.google.com/rss/search?q=%22Tiburones+de+La+Guaira%22&hl=es&gl=VE&ceid=VE:es"

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    img_data = requests.get(url_img, headers=headers, timeout=15).content
    files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
    data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
    r = requests.post(url, files=files, data=data, timeout=20)
    print("Foto enviada: " + str(r.status_code))

def main():
    print("Iniciando bot...")
    response = requests.get(RSS_URL, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('item')
    
    for item in items[:3]:
        titulo = item.find('title').get_text(strip=True)
        content = str(item.find('content')) if item.find('content') else ""
        img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
        imagen = img_match.group(1) if img_match else None
        descripcion = BeautifulSoup(content, 'html.parser').get_text(strip=True)[:300]
        
        texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>\n\n" + descripcion
        
        if imagen:
            enviar_foto(imagen, texto)
        else:
            enviar_foto(LOGO, texto)
        print("Noticia publicada: " + titulo[:50])
    
    link_cal = "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
    texto_cal = "📅 <b>CALENDARIO LVBP - SEMANA 1</b>\n\n🏟️ Todos los juegos del 12-16 de octubre\n\n⚾ Temporada 2026-2027"
    enviar_foto(link_cal, texto_cal)
    print("Proceso terminado.")

if __name__ == '__main__':
    main()
