import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    r = requests.post(url, data=datos, timeout=15)
    print("Enviado: " + str(r.status_code))

def enviar_foto(url_foto, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    img_data = requests.get(url_foto, headers=headers, timeout=15).content
    files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
    data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
    r = requests.post(url, files=files, data=data, timeout=20)
    print("Foto: " + str(r.status_code))

def main():
    print("Iniciando bot...")
    total = 0
    
    # PARTE 1: NOTICIAS
    print("Buscando noticias...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        html = page.content()
        browser.close()
    
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    if len(articles) == 0:
        articles = soup.find_all('div')
    
    for art in articles[:3]:
        img_tag = art.find('img')
        img_url = None
        if img_tag:
            img_url = img_tag.get('src')
            if img_url and not img_url.startswith('http'):
                img_url = 'https://www.tiburonesbbc.com' + img_url
        titulo_tag = art.find(['h1', 'h2', 'h3'])
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
        p_tag = art.find('p')
        resumen = p_tag.get_text(strip=True)[:200] if p_tag else ""
        if titulo and len(titulo) > 10:
            texto = "🦈 <b>TIBURONES</b>\n\n<b>" + titulo + "</b>\n\n" + resumen
            if img_url:
                enviar_foto(img_url, texto)
            else:
                enviar_texto(texto)
            total += 1
    
    # PARTE 2: CALENDARIO (SOLO TEXTO, SIN IMAGEN)
    print("Publicando calendario en texto...")
    calendario = """🦈 <b>CALENDARIO TIBURONES - OCTUBRE 2026</b>

 <b>SEMANA 1:</b>
🔴 Mar 13: vs MAGALLANES
🔴 Jue 15: vs ANZOÁTEGUI
🔴 Vie 16: vs ANZOÁTEGUI
 Sáb 17: vs ARAGUA
⚪ Dom 18: vs ARAGUA

📅 <b>SEMANA 2:</b>
🔴 Mar 20: vs CARACAS
⚪ Mie 21: vs MAGALLANES
⚪ Jue 22: vs MARGARITA
 Vie 23: vs MARGARITA
🔴 Sáb 24: vs ANZOÁTEGUI
🔴 Dom 25: vs ANZOÁTEGUI

📅 <b>SEMANA 3:</b>
 Mar 27: vs MAGALLANES
⚪ Mie 28: vs CARACAS
🔴 Jue 29: vs LARA
🔴 Vie 30: vs ZULIA
⚪ Sáb 31: vs LARA

🔴 Rojo = Local | ⚪ Visita
¡Que comience la temporada! ⚾"""
    
    enviar_texto(calendario)
    total += 1
    
    if total == 0:
        enviar_texto("🦈 <b>TIBURONES</b>\n\n⚾ Información próximamente.")
    
    print("Total publicaciones: " + str(total))

if __name__ == '__main__':
    main()import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    r = requests.post(url, data=datos, timeout=15)
    print("Enviado: " + str(r.status_code))

def enviar_foto(url_foto, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    img_data = requests.get(url_foto, headers=headers, timeout=15).content
    files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
    data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
    r = requests.post(url, files=files, data=data, timeout=20)
    print("Foto: " + str(r.status_code))

def main():
    print("Iniciando bot...")
    total = 0
    
    # PARTE 1: NOTICIAS
    print("Buscando noticias...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        html = page.content()
        browser.close()
    
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    if len(articles) == 0:
        articles = soup.find_all('div')
    
    for art in articles[:3]:
        img_tag = art.find('img')
        img_url = None
        if img_tag:
            img_url = img_tag.get('src')
            if img_url and not img_url.startswith('http'):
                img_url = 'https://www.tiburonesbbc.com' + img_url
        titulo_tag = art.find(['h1', 'h2', 'h3'])
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
