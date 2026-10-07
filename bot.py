import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, data=datos, timeout=15)
        print("Texto enviado: " + str(r.status_code))
    except Exception as e:
        print("Error: " + str(e))

def enviar_foto(url_foto, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_data = requests.get(url_foto, headers=headers, timeout=15).content
        files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=20)
        print("Foto enviada: " + str(r.status_code))
    except Exception as e:
        print("Error foto: " + str(e))
        enviar_texto(texto)

def obtener_noticias_tiburones():
    print("Buscando noticias de Tiburones...")
    enviadas = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
            time.sleep(5)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('div', class_=re.compile('card|post|news', re.I))
            
            for art in articles[:3]:
                try:
                    img_tag = art.find('img')
                    img_url = None
                    if img_tag:
                        img_url = img_tag.get('src') or img_tag.get('data-src')
                        if img_url and not img_url.startswith('http'):
                            img_url = 'https://www.tiburonesbbc.com' + img_url
                    
                    titulo_tag = art.find(['h1', 'h2', 'h3', 'h4'])
                    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
                    
                    p_tag = art.find('p')
                    resumen = p_tag.get_text(strip=True)[:200] if p_tag else ""
                    
                    if titulo and len(titulo) > 10:
                        texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>\n\n" + resumen
                        if img_url:
                            enviar_foto(img_url, texto)
                        else:
                            enviar_texto(texto)
                        enviadas += 1
                except Exception as e:
                    continue
                    
        except Exception as e:
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, data=datos, timeout=15)
        print("Texto enviado: " + str(r.status_code))
    except Exception as e:
        print("Error: " + str(e))

def enviar_foto(url_foto, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        img_data = requests.get(url_foto, headers=headers, timeout=15).content
        files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=20)
        if r.status_code == 200:
            print("Foto enviada correctamente")
        else:
            print("Error foto: " + str(r.status_code))
            enviar_texto(texto)
    except Exception as e:
        print("Error foto: " + str(e))
        enviar_texto(texto)

def obtener_noticias_tiburones():
    print("Buscando noticias de Tiburones...")
    enviadas = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
            time.sleep(5)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('div', class_=re.compile('card|post|news', re.I))
            if not articles:
                articles = soup.find_all('div')
            
            for art in articles[:3]:
                try:
                    img_tag = art.find('img')
                    img_url = None
                    if img_tag:
                        img_url = img_tag.get('src') or img_tag.get('data-src')
                        if img_url and not img_url.startswith('http'):
                            img_url = 'https://www.tiburonesbbc.com' + img_url
                    
                    titulo_tag = art.find(['h1', 'h2', 'h3', 'h4'])
                    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
                    
                    p_tag = art.find('p')
                    resumen = p_tag.get_text(strip=True)[:200] if p_tag else ""
                    
                    if titulo and len(titulo) > 10:
                        texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>\n\n" + resumen
                        if img_url:
                            enviar_foto(img_url, texto)
                        else:
                            enviar_texto(texto)
                        enviadas += 1
                except Exception as e:
                    continue
                    
        except Exception as e:
            print("Error Playwright: " + str(e))
        finally:
            browser.close()
    
    return enviadas

def obtener_calendario_tiburones():
    print("Buscando calendario...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://www.tiburonesbbc.com/calendario', wait_until='networkidle', timeout=30000)
            time.sleep(5)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            imgs = soup.find_all('img')
            img_cal = None
            
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and ('calendario' in src.lower() or 'octubre' in src.lower()):
                    img_cal = src
                    break
            
            if not img_cal:
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and src.startswith('http') and len(src) > 30:
                        img_cal = src
                        break
            
            if img_cal:
                if not img_cal.startswith('http'):
                    img_cal = 'https://www.tiburonesbbc.com' + img_cal
                
                texto = "🦈 <b>CALENDARIO TIBURONES 2026-2027</b>\n\n📅 Rojo = Local | Blanco = Visita\n\n¡Que comience la temporada!"
                enviar_foto(img_cal, texto)
                return True
            else:
                calendario_texto = """🦈 <b>CALENDARIO TIBURONES - OCTUBRE 2026</b>

📅 <b>SEMANA 1:</b>
🔴 Mar 13: vs MAGALLANES (Local)
 Mie 14: DESCANSO
🔴 Jue 15: vs ANZOÁTEGUI (Local)
 Vie 16: vs ANZOÁTEGUI (Local)
⚪ Sáb 17: vs ARAgua (Visita)
 Dom 18: vs ARAGUA (Visita)

📅 <b>SEMANA 2:</b>
⚪ Lun 19: DESCANSO
🔴 Mar 20: vs CARACAS (Local)
⚪ Mie 21: vs MAGALLANES (Visita)
⚪ Jue 22: vs MARGARITA (Visita)
⚪ Vie 23: vs MARGARITA (Visita)
🔴 Sáb 24: vs ANZOÁTEGUI (Local)
🔴 Dom 25: vs ANZOÁTEGUI (Local)

 <b>SEMANA 3:</b>
⚪ Lun 26: DESCANSO
🔴 Mar 27: vs MAGALLANES (Local)
⚪ Mie 28: vs CARACAS (Visita)
 Jue 29: vs LARA (Local)
🔴 Vie 30: vs ZULIA (Local)
⚪ Sáb 31: vs LARA (Visita)

🔴 Rojo = Juegos de local en La Guaira
⚪ Blanco = Juegos de visita

¡Que comience la temporada! ⚾"""
                enviar_texto(calendario_texto)
                return True
                
        except Exception as e:
            print("Error calendario: " + str(e))
        finally:
            browser.close()
    
    return False

def main():
    print("Bot Tiburones iniciado")
    total = 0
    
    noticias = obtener_noticias_tiburones()
    total += noticias
    print("Noticias: " + str(noticias))
    
    if obtener_calendario_tiburones():
        total += 1
    
    if total == 0:
        enviar_texto("🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n Información próximamente.")
    
    print("Total: " + str(total))

if __name__ == '__main__':
    main()
