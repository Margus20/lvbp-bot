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
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import datetime

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

LOGO_TIBURONES = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

def enviar_foto(url_imagen, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        imagen = requests.get(url_imagen, timeout=10).content
        files = {'photo': ('imagen.jpg', imagen, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=20)
        print("✅ Foto enviada a Telegram: " + str(r.status_code))
    except Exception as e:
        print("❌ Error enviando foto: " + str(e))

def enviar_noticias_con_logo():
    print("🔍 MODO DETECTIVE: Entrando a la web de noticias...")
    total = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        html = page.content()
        browser.close()
    
    # 1. Verificar si la página cargó
    print("📏 Tamaño del código HTML descargado: " + str(len(html)) + " caracteres")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 2. Buscar TODOS los posibles títulos
    posibles_titulos = soup.find_all(['h1', 'h2', 'h3', 'h4', 'a', 'span'])
    titulos_encontrados = []
    for t in posibles_titulos:
        texto = t.get_text(strip=True)
        if len(texto) > 15 and len(texto) < 100: # Filtramos textos muy cortos o muy largos
            titulos_encontrados.append(texto)
    
    # Eliminamos duplicados
    titulos_unicos = list(dict.fromkeys(titulos_encontrados))[:5] # Solo los primeros 5
    
    print("📰 TÍTULOS QUE EL BOT PUDO LEER:")
    for i, titulo in enumerate(titulos_unicos):
        print(f"   {i+1}. {titulo}")
    
    if len(titulos_unicos) == 0:
        print("⚠️ ADVERTENCIA: El bot NO encontró ningún título. La página podría estar bloqueando al robot o usando una estructura muy rara.")
        return 0

    # 3. Intentar publicar el primero que encontremos
    if len(titulos_unicos) > 0:
        mejor_titulo = titulos_unicos[0]
        texto_publicar = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + mejor_titulo + "</b>\n\n🔗 Fuente: tiburonesbbc.com"
        print("📤 Intentando publicar: " + mejor_titulo)
        enviar_foto(LOGO_TIBURONES, texto_publicar)
        total += 1
    
    return total

def main():
    print("🤖 Iniciando bot...")
    total = 0
    
    # 1. Noticias
    noticias = enviar_noticias_con_logo()
    total += noticias
    
    # 2. Calendario (Forzamos la imagen que ya probamos)
    link_calendario = "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
    texto_cal = "📅 <b>CALENDARIO TIBURONES - OCTUBRE 2026</b>\n\nSemana 1: 12-16 de octubre\n\n¡Que comience la temporada! ⚾"
    enviar_foto(link_calendario, texto_cal)
    total += 1
    
    print("🏁 Proceso terminado. Total publicaciones: " + str(total))

if __name__ == '__main__':
    main()
