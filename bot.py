import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# Configuración
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def enviar_foto(url_foto, texto):
    """Envía una foto con texto al canal"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
    try:
        img_data = requests.get(url_foto, headers=HEADERS, timeout=10).content
        files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        
        respuesta = requests.post(url, files=files, data=data, timeout=15)
        if respuesta.status_code == 200:
            print(f"✅ Foto enviada correctamente")
            return True
        else:
            print(f"❌ Error enviando foto")
            enviar_texto(texto)
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        enviar_texto(texto)

def enviar_texto(texto):
    """Envía solo texto al canal"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=datos, timeout=15)
        print(f"✅ Mensaje enviado")
    except Exception as e:
        print(f"❌ Error: {e}")

def obtener_noticias_tiburones():
    """Busca noticias en la página de Tiburones"""
    print("🦈 Buscando noticias de Tiburones...")
    enviadas = 0
    
    try:
        response = requests.get('https://www.tiburonesbbc.com/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar artículos (estructuras comunes)
        articulos = soup.find_all('article')
        if not articulos:
            articulos = soup.find_all('div', class_='post')
        if not articulos:
            articulos = soup.find_all('div', class_='entry')
        if not articulos:
            articulos = soup.find_all('a', href=re.compile('noticia|news|article', re.I))
        
        for art in articulos[:3]:  # Máximo 3 noticias
            try:
                # Título
                titulo_tag = art.find(['h2', 'h3', 'h4'])
                if not titulo_tag:
                    titulo_tag = art.find('a')
                if titulo_tag:
                    titulo = titulo_tag.get_text(strip=True)
                else:
                    continue
                
                # Imagen
                img_tag = art.find('img')
                img_url = None
                if img_tag:
                    img_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src')
                    if img_url and not img_url.startswith('http'):
                        img_url = 'https://www.tiburonesbbc.com' + img_url
                
                # Resumen
                p_tag = art.find('p')
                resumen = p_tag.get_text(strip=True)[:200] + "..." if p_tag else ""
                
                if titulo and len(titulo) > 10:
                    texto = f"🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>{titulo}</b>\n\n{resumen}" if resumen else f"🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>{titulo}</b>"
                    
                    if img_url:
                        enviar_foto(img_url, texto)
                    else:
                        enviar_texto(texto)
                    
                    enviadas += 1
            except Exception as e:
                continue
                
    except Exception as e:
        print(f" Error buscando noticias: {e}")
    
    return enviadas

def obtener_resultados_tiburones():
    """Busca resultados de juegos de Tiburones"""
    print("🦈 Buscando resultados de Tiburones...")
    
    try:
        response = requests.get('https://www.tiburonesbbc.com/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar secciones de resultados o marcadores
        resultados = []
        
        # Buscar en diferentes estructuras posibles
        secciones = soup.find_all(['div', 'section'], class_=re.compile('result|score|game|match|juego', re.I))
        
        for sec in secciones[:3]:
            texto = sec.get_text(strip=True)
            if texto and ('Tibur' in texto or 'Guaira' in texto or len(texto) < 100):
                resultados.append(texto[:150])
        
        if resultados:
            texto_final = " <b>RESULTADOS TIBURONES</b>\n\n"
            texto_final += '\n'.join(resultados[:3])
            enviar_texto(texto_final)
            return True
        else:
            # Si no encuentra resultados específicos, buscar en el contenido general
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# Configuración
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def enviar_foto(url_foto, texto):
    """Envía una foto con texto al canal"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
    try:
        img_data = requests.get(url_foto, headers=HEADERS, timeout=15).content
        files = {'photo': ('image.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        
        respuesta = requests.post(url, files=files, data=data, timeout=20)
        if respuesta.status_code == 200:
            print(f"✅ Foto enviada correctamente")
            return True
        else:
            print(f"❌ Error enviando foto: {respuesta.status_code}")
            enviar_texto(texto)
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        enviar_texto(texto)

def enviar_texto(texto):
    """Envía solo texto al canal"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    try:
        respuesta = requests.post(url, data=datos, timeout=15)
        print(f"✅ Mensaje enviado")
    except Exception as e:
        print(f"❌ Error: {e}")

def obtener_noticias_tiburones():
    """Busca noticias en /noticias"""
    print("🦈 Buscando noticias en tiburonesbbc.com/noticias...")
    enviadas = 0
    
    try:
        response = requests.get('https://www.tiburonesbbc.com/noticias', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar contenedores de noticias (basado en la estructura visual)
        # Buscamos divs que contengan imágenes y texto
        noticias = soup.find_all('div', class_=re.compile('card|post|article|news', re.I))
        
        if not noticias:
            # Intento alternativo: buscar por estructura de imagen + texto
            noticias = soup.find_all('div', style=re.compile('margin|padding', re.I))
        
        if not noticias:
            # Último intento: buscar todos los divs y filtrar
            noticias = soup.find_all('div')
        
        for noticia in noticias[:3]:  # Máximo 3 noticias
            try:
                # Buscar imagen
                img_tag = noticia.find('img')
                img_url = None
                if img_tag:
                    img_url = img_tag.get('src') or img_tag.get('data-src')
                    if img_url and not img_url.startswith('http'):
                        img_url = 'https://www.tiburonesbbc.com' + img_url
                
                # Buscar título (texto en mayúsculas o negrita)
                titulo = None
                titulo_tag = noticia.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                if titulo_tag:
                    titulo = titulo_tag.get_text(strip=True)
                
                # Buscar fecha
                fecha = None
                fecha_texto = noticia.find(text=re.compile('\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2}'))
                if fecha_texto:
                    fecha = fecha_texto.strip()
                
                # Buscar resumen (párrafo después del título)
                resumen = ""
                p_tags = noticia.find_all('p')
                for p in p_tags:
                    texto_p = p.get_text(strip=True)
                    if len(texto_p) > 20 and len(texto_p) < 300:
                        resumen = texto_p[:200]
                        break
                
                # Si encontramos los elementos clave
                if titulo and len(titulo) > 10:
                    texto = f" <b>TIBURONES DE LA GUAIRA</b>\n\n"
                    if fecha:
                        texto += f"📅 {fecha}\n\n"
                    texto += f"<b>{titulo}</b>\n\n"
                    if resumen:
                        texto += resumen
                    
                    if img_url:
                        enviar_foto(img_url, texto)
                    else:
                        enviar_texto(texto)
                    
                    enviadas += 1
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"❌ Error buscando noticias: {e}")
    
    return enviadas

def obtener_calendario_tiburones():
    """Descarga y publica la imagen del calendario"""
    print("🦈 Buscando calendario...")
    
    try:
        response = requests.get('https://www.tiburonesbbc.com/calendario', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la imagen del calendario
        img_calendario = None
        
        # Buscar imágenes que parezcan el calendario
        imgs = soup.find_all('img')
        for img in imgs:
            src = img.get('src') or img.get('data-src')
            if src and ('calendario' in src.lower() or 'octubre' in src.lower() or 'schedule' in src.lower()):
                img_calendario = src
                break
        
        # Si no encuentra por nombre, buscar la imagen más grande
        if not img_calendario:
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    img_calendario = src
                    break
        
        if img_calendario:
            if not img_calendario.startswith('http'):
                img_calendario = 'https://www.tiburonesbbc.com' + img_calendario
            
            texto = "🦈 <b>CALENDARIO TIBURONES DE LA GUAIRA</b>\n\n📅 Temporada 2026-2027\n\n Rojo = Juegos de local\n Blanco = Juegos de visita\n\n ¡Que comience la temporada!"
            enviar_foto(img_calendario, texto)
            return True
        else:
            enviar_texto("🦈 <b>CALENDARIO TIBURONES</b>\n\n📅 El calendario visual estará disponible próximamente.\n\n🔔 Activa las notificaciones para no perderte ningún juego.")
            return True
            
    except Exception as e:
        print(f"❌ Error buscando calendario: {e}")
    
    return False

def main():
    print(f"🤖 Bot Tiburones - {datetime.now()}")
    print("=" * 50)
    
    total = 0
    
    # 1. Noticias
    noticias = obtener_noticias_tiburones()
    total += noticias
    print(f"📰 Noticias publicadas: {noticias}")
    
    # 2. Calendario (imagen)
    if obtener_calendario_tiburones():
        total += 1
        print(f"📅 Calendario publicado")
    
    if total == 0:
        enviar_texto("🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n⚾ Información próximamente disponible.\n\n🔔 Activa notificaciones para no perderte nada.")
    
    print(f"✅ Completado. Total publicaciones: {total}")
    print("=" * 50)

if __name__ == '__main__':
    main()
