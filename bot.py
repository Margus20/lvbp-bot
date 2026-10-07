import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def enviar_foto(url_foto, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        img_data = requests.get(url_foto, headers=HEADERS, timeout=15).content
        files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        r = requests.post(url, files=files, data=data, timeout=20)
        if r.status_code == 200:
            print("Foto enviada")
        else:
            enviar_texto(texto)
    except Exception as e:
        print("Error foto: " + str(e))
        enviar_texto(texto)

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=datos, timeout=15)
        print("Texto enviado")
    except Exception as e:
        print("Error texto: " + str(e))

def obtener_noticias_tiburones():
    print("Buscando noticias de Tiburones...")
    enviadas = 0
    try:
        r = requests.get('https://www.tiburonesbbc.com/noticias', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        noticias = soup.find_all('div', class_=re.compile('card|post|article|news', re.I))
        if not noticias:
            noticias = soup.find_all('div')
        for n in noticias[:3]:
            try:
                img_tag = n.find('img')
                img_url = None
                if img_tag:
                    img_url = img_tag.get('src') or img_tag.get('data-src')
                    if img_url and not img_url.startswith('http'):
                        img_url = 'https://www.tiburonesbbc.com' + img_url
                titulo_tag = n.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
                p_tag = n.find('p')
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
        print("Error noticias: " + str(e))
    return enviadas

def obtener_calendario_tiburones():
    print("Buscando calendario...")
    try:
        r = requests.get('https://www.tiburonesbbc.com/calendario', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
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
            enviar_texto("🦈 <b>CALENDARIO TIBURONES</b>\n\n📅 Próximamente disponible.\n\n🔔 Activa notificaciones.")
            return True
    except Exception as e:
        print("Error calendario: " + str(e))
    return False

def main():
    print("Bot Tiburones iniciado")
    total = 0
    noticias = obtener_noticias_tiburones()
    total += noticias
    print("Noticias: " + str(noticias))
    if obtener_calendario_tiburones():
        total += 1
        print("Calendario publicado")
    if total == 0:
        enviar_texto("🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n⚾ Información próximamente.\n\n Activa notificaciones.")
    print("Total publicaciones: " + str(total))

if __name__ == '__main__':
    main()
