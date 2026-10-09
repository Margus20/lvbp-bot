import os
import re
import time
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBpalDia'
VISTOS_FILE = 'vistos.txt'
CALENDARIO_FILE = 'calendario.json'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

LOGOS = {
    'tiburones': 'https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png',
    'aguilas': 'https://i.postimg.cc/J4wxQnwX/1791392132263-11zon.jpg',
    'tigres': 'https://i.postimg.cc/0QRG0W3n/1791393470300-11zon.jpg',
    'caribes': 'https://i.postimg.cc/0j685n5D/image-search-1791393733450-11zon.webp',
    'bravos': 'https://i.postimg.cc/PJh5yYdY/1791395148443-11zon.jpg',
    'cardenales': 'https://i.postimg.cc/HLpzqP32/image-search-1791395610326-11zon.jpg',
    'navegantes': 'https://i.postimg.cc/ydNH8j6v/1791396497437-11zon.jpg',
    'leones': 'https://i.postimg.cc/Kjrw7g8p/image-search-1791396859705.jpg',
    'general': 'https://i.postimg.cc/T29t9x9M/image-search-1791397173263.jpg'
}

EQUIPOS = {
    'tiburones': {'nombres': ['tiburones de la guaira', 'tiburones lvg']},
    'aguilas': {'nombres': ['aguilas del zulia', 'aguilas zulia']},
    'tigres': {'nombres': ['tigres de aragua', 'tigres aragua']},
    'caribes': {'nombres': ['caribes de anzoategui', 'caribes anzoategui']},
    'bravos': {'nombres': ['bravos de margarita', 'bravos margarita']},
    'cardenales': {'nombres': ['cardenales de lara', 'cardenales lara']},
    'navegantes': {'nombres': ['navegantes del magallanes', 'navegantes magallanes']},
    'leones': {'nombres': ['leones del caracas', 'leones caracas']}
}

# LAS 9 PÁGINAS WEB OFICIALES QUE TÚ ME DISTE
PAGINAS = {
    'lvbp': 'https://lvbp.com/',
    'leones': 'https://leones.com/',
    'navegantes': 'https://magallanesbbc.com.ve/',
    'tiburones': 'https://www.tiburonesbbc.com/',
    'aguilas': 'https://aguilas.com/',
    'tigres': 'https://tigresdearaguabbc.com/',
    'caribes': 'https://caribesbbc.com/',
    'cardenales': 'https://cardenalesdelara.com/',
    'bravos': 'https://bravosdemargarita.com/'
}

# LOS 9 CANALES DE YOUTUBE QUE TÚ ME DISTE (handles)
YOUTUBE_HANDLES = {
    'lvbp': '@lvbp_oficial',
    'leones': '@teleleones_cbbc',
    'navegantes': '@magallanesbbcoficial',
    'tiburones': '@tiburonesbbc_',
    'tigres': '@circuitoradialtigresdearagua',
    'aguilas': '@aguilasdelzuliabbc',
    'cardenales': '@cardenalesbbc',
    'bravos': '@bravosesmargaritatv',
    'beisbolplay': '@beisbolplay'
}

# Cache para almacenar channel_ids
channel_id_cache = {}

def limpiar(txt):
    txt = re.sub(r'https?://\S+', '', txt)
    txt = re.sub(r'www\.\S+', '', txt)
    return re.sub(r'\s+', ' ', txt).strip()

def cargar_vistos():
    if os.path.exists(VISTOS_FILE):
        with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def guardar_visto(norm):
    with open(VISTOS_FILE, 'a', encoding='utf-8') as f:
        f.write(norm + '\n')

def obtener_channel_id(handle):
    """Obtiene el channel_id de YouTube desde el handle (@nombre)"""
    if handle in channel_id_cache:
        return channel_id_cache[handle]
    
    try:
        # YouTube redirige del handle al channel_id
        url = f"https://www.youtube.com/{handle}"
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        
        # Buscar el channel_id en el HTML
        match = re.search(r'"channelId":"(UC[^"]+)"', resp.text)
        if match:
            channel_id = match.group(1)
            channel_id_cache[handle] = channel_id
            print(f"  ✅ {handle} -> {channel_id}")
            return channel_id
    except Exception as e:
        print(f"  ⚠️ Error obteniendo ID de {handle}: {e}")
    
    return None

def enviar_foto(url, texto, logo):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if url and url.startswith('http'):
        try:
            img = requests.get(url, headers=headers, timeout=10).content
            files = {'photo': ('i.jpg', img, 'image/jpeg')}
            data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
            r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', files=files, data=data, timeout=15)
            if r.status_code == 200:
                return True
        except Exception:
            pass
    
    try:
        img = requests.get(logo, headers=headers, timeout=10).content
        files = {'photo': ('logo.jpg', img, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
        requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', files=files, data=data, timeout=15)
        return True
    except Exception:
        return False

def enviar_mensaje(texto):
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data, timeout=10)
    return r.status_code == 200

def detectar(titulo):
    t = titulo.lower()
    for eq, datos in EQUIPOS.items():
        for nombre in datos['nombres']:
            if nombre in t:
                return eq
    return 'general'

def obtener_noticias_pagina(equipo_key, url_base):
    """Obtiene noticias de una página web CON ENLACE"""
    noticias = []
    try:
        resp = requests.get(url_base, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar artículos/noticias
        for art in soup.find_all(['article', 'div'], class_=re.compile('post|news|article', re.I))[:15]:
            tag = art.find(['h2', 'h3', 'a'])
            if tag:
                tit = limpiar(tag.get_text(strip=True))
                if len(tit) > 15:
                    # Obtener enlace
                    enlace = url_base
                    if tag.name == 'a' and tag.get('href'):
                        enlace = urljoin(url_base, tag.get('href'))
                    elif art.find('a') and art.find('a').get('href'):
                        enlace = urljoin(url_base, art.find('a').get('href'))
                    
                    desc = limpiar(art.find('p').get_text(strip=True)[:200]) if art.find('p') else ''
                    img = art.find('img')
                    img_url = urljoin(url_base, img.get('src')) if img and img.get('src') else None
                    
                    noticias.append({
                        'titulo': tit,
                        'desc': desc,
                        'img': img_url,
                        'enlace': enlace,
                        'eq': detectar(tit),
                        'tipo': 'web'
                    })
    except Exception as e:
        print(f"Error {equipo_key}: {e}")
    return noticias

def obtener_videos_youtube(handle, equipo_key):
    """Obtiene videos de un canal de YouTube CON MINIATURA Y ENLACE"""
    videos = []
    
    # Obtener channel_id
    channel_id = obtener_channel_id(handle)
    if not channel_id:
        return videos
    
    # Obtener feed RSS de YouTube
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'yt': 'http://www.youtube.com/xml/schemas/2015',
                'media': 'http://search.yahoo.com/mrss/'
            }
            
            entries = root.findall('atom:entry', ns)
            for entry in entries[:5]:  # Últimos 5 videos
                video_id = entry.find('yt:videoId', ns).text
                titulo = entry.find('atom:title', ns).text
                link = entry.find('atom:link', ns).attrib['href']
                
                # Obtener miniatura
                thumbnail = entry.find('media:group/media:thumbnail', ns)
                img_url = thumbnail.get('url') if thumbnail is not None else f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                
                videos.append({
                    'titulo': titulo,
                    'desc': f"Ver video completo en YouTube",
                    'img': img_url,
                    'enlace': link,
                    'eq': detectar(titulo),
                    'tipo': 'youtube',
                    'id': f"yt_{video_id}"
                })
    except Exception as e:
        print(f"Error YouTube {handle}: {e}")
    
    return videos

def obtener_jornada_hoy():
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with open(CALENDARIO_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for semana in data.get('calendario', []):
            if semana.get('fecha_inicio') <= hoy <= semana.get('fecha_fin'):
                return semana
        for semana in data.get('calendario', []):
            if semana.get('activo'):
                return semana
    except Exception as e:
        print(f"Error calendario: {e}")
    return None

def obtener_posiciones():
    try:
        resp = requests.get('https://www.lvbp.com/posiciones/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tabla = soup.find('table', class_=re.compile('standings|tabla|posiciones', re.I))
        if tabla:
            filas = tabla.find_all('tr')[1:6]
            posiciones = []
            for fila in filas:
                cols = fila.find_all('td')
                if len(cols) >= 3:
                    equipo = cols[1].get_text(strip=True)
                    ganados = cols[2].get_text(strip=True)
                    perdidos = cols[3].get_text(strip=True) if len(cols) > 3 else '0'
                    posiciones.append(f"{equipo}: {ganados}G-{perdidos}P")
            return posiciones
    except Exception as e:
        print(f"Error posiciones: {e}")
    return None

def main():
    print("⚾ Iniciando bot LVBP (SOLO fuentes oficiales)...")
    vistos = cargar_vistos()
    todas_las_noticias = []
    
    # 1. Obtener noticias de las 9 páginas web CON ENLACE
    print("🌐 Buscando en páginas web oficiales...")
    for eq, url in PAGINAS.items():
        print(f"  - {eq}: {url}")
        todas_las_noticias.extend(obtener_noticias_pagina(eq, url))
    
    # 2. Obtener videos de los 9 canales de YouTube CON MINIATURA Y ENLACE
    print("📺 Buscando en canales de YouTube...")
    for eq, handle in YOUTUBE_HANDLES.items():
        print(f"  - {eq}: {handle}")
        todas_las_noticias.extend(obtener_videos_youtube(handle, eq))
    
    # 3. Filtrar noticias nuevas (SIN LÍMITE)
    print(f"📊 Total de noticias encontradas: {len(todas_las_noticias)}")
    finales = []
    for n in todas_las_noticias:
        norm = re.sub(r'[^a-z0-9]', '', n['titulo'].lower())
        if norm not in vistos and len(norm) > 15:
            vistos.add(norm)
            finales.append((norm, n))
    
    print(f"✅ Noticias nuevas a publicar: {len(finales)}")
    
    # 4. Publicar TODAS las noticias nuevas CON ENLACE
    for norm, n in finales:
        logo = LOGOS.get(n['eq'], LOGOS['general'])
        
        if n['tipo'] == 'youtube':
            texto = f"📺 <b>{n['titulo']}</b>\n\n{n['desc']}\n\n🔗 {n['enlace']}"
        else:
            texto = f" <b>{n['titulo']}</b>\n\n{n['desc']}\n\n🔗 {n['enlace']}"
        
        if enviar_foto(n.get('img'), texto, logo):
            guardar_visto(norm)
            print(f"✅ Publicada: {n['titulo'][:40]}")
            time.sleep(2)
    
    # 5. Publicar jornada del día
    print(" Verificando jornada de hoy...")
    jornada = obtener_jornada_hoy()
    if jornada:
        texto_jornada = f" <b>{jornada.get('titulo', 'JORNADA DE HOY')}</b>\n\n{jornada.get('descripcion', 'Partidos de hoy')}"
        if enviar_foto(jornada.get('imagen'), texto_jornada, LOGOS['general']):
            print("📅 Jornada publicada")
            time.sleep(2)
    
    # 6. Publicar posiciones (cada 3 días)
    hoy_num = datetime.now().day
    if hoy_num % 3 == 0:
        print(" Obteniendo posiciones...")
        posiciones = obtener_posiciones()
        if posiciones:
            texto_pos = "🏆 <b>POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
            if enviar_mensaje(texto_pos):
                print("🏆 Posiciones publicadas")
                time.sleep(2)
    
    print("✅ Terminado - SOLO contenido LVBP oficial")

if __name__ == '__main__':
    main()
