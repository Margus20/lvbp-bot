import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time
import datetime

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

# Logo de los Tiburones
LOGO_TIBURONES = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

# Calendario semanal
CALENDARIO_SEMANAS = {
    "2026-10-12": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg",
    "2026-10-19": "AQUI_PEGA_EL_LINK_DE_LA_SEMANA_2",
    "2026-10-26": "AQUI_PEGA_EL_LINK_DE_LA_SEMANA_3",
    "2026-11-02": "AQUI_PEGA_EL_LINK_DE_LA_SEMANA_4",
}

def enviar_foto(url_imagen, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        imagen = requests.get(url_imagen).content
        files = {'photo': ('imagen.jpg', imagen, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=20)
        print("Enviado: " + str(r.status_code))
    except Exception as e:
        print("Error: " + str(e))

def enviar_noticias_con_logo():
    print("Buscando noticias...")
    total = 0
    
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
        titulo_tag = art.find(['h1', 'h2', 'h3'])
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
        p_tag = art.find('p')
        resumen = p_tag.get_text(strip=True)[:250] if p_tag else ""
        
        if titulo and len(titulo) > 10:
            texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>\n\n" + resumen + "\n\n🔗 Fuente: tiburonesbbc.com"
            enviar_foto(LOGO_TIBURONES, texto)
            total += 1
    
    return total

def publicar_calendario_semanal():
    print("Buscando calendario de la semana...")
    
    hoy = datetime.date.today().isoformat()
    semana_a_publicar = None
    
    for fecha in sorted(CALENDARIO_SEMANAS.keys()):
        if fecha <= hoy:
            semana_a_publicar = fecha
        else:
            break
    
    if semana_a_publicar:
        link = CALENDARIO_SEMANAS[semana_a_publicar]
        texto = " <b>CALENDARIO TIBURONES - SEMANA DEL " + semana_a_publicar + "</b>\n\n¡Que comience la acción! ⚾"
        enviar_foto(link, texto)
        print("Calendario de la semana " + semana_a_publicar + " publicado")
    else:
        print("No hay calendario para esta fecha")

def main():
    print("Iniciando bot...")
    total = 0
    
    # 1. Publicar noticias con logo
    noticias = enviar_noticias_con_logo()
    total += noticias
    
    # 2. Publicar calendario de la semana
    publicar_calendario_semanal()
    total += 1
    
    print("Total publicaciones: " + str(total))

if __name__ == '__main__':
    main()
