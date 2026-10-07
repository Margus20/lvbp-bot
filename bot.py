import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
LOGO = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    img_data = requests.get(url_img, timeout=10).content
    files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
    data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
    r = requests.post(url, files=files, data=data, timeout=20)
    print("Status foto: " + str(r.status_code))

def main():
    print("Iniciando bot...")
    
    # 1. Entrar a la web
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        html = page.content()
        browser.close()

    print("Tamaño HTML: " + str(len(html)))
    soup = BeautifulSoup(html, 'html.parser')
    
    # 2. Buscar títulos
    titulos = soup.find_all(['h1', 'h2', 'h3', 'a', 'span'])
    encontrados = []
    for t in titulos:
        txt = t.get_text(strip=True)
        if len(txt) > 15 and len(txt) < 100:
            if txt not in encontrados:
                encontrados.append(txt)

    print("TITULOS ENCONTRADOS POR EL BOT:")
    for i, t in enumerate(encontrados[:3]):
        print(str(i+1) + ". " + t)
        texto = "🦈 <b>TIBURONES</b>\n\n<b>" + t + "</b>\n\n🔗 tiburonesbbc.com"
        enviar_foto(LOGO, texto)

    # 3. Publicar Calendario
    link_cal = "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
    texto_cal = "📅 <b>CALENDARIO TIBURONES - OCTUBRE 2026</b>\n\nSemana 1: 12-16 de octubre"
    enviar_foto(link_cal, texto_cal)
    
    print("Proceso terminado.")

if __name__ == '__main__':
    main()
