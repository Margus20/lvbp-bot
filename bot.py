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
CHANNEL = '@LVBPAIDia'
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

# NOMBRES COMPLETOS Y ESPECÍFICOS para evitar confusiones con otros equipos
EQUIPOS = {
    'tiburones': {
        'nombres': ['tiburones de la guaira', 'tiburones lvg', 'tiburones de la guaira bbc'],
        'busqueda_google': 'tiburones de la guaira beisbol venezuela'
    },
    'aguilas': {
        'nombres': ['aguilas del zulia', 'aguilas del zulia bbc', 'aguilas zulia'],
        'busqueda_google': 'aguilas del zulia beisbol venezuela'
    },
    'tigres': {
        'nombres': ['tigres de aragua', 'tigres de aragua bbc', 'tigres aragua'],
        'busqueda_google': 'tigres de aragua beisbol venezuela'
    },
    'caribes': {
        'nombres': ['caribes de anzoategui', 'caribes de anzoategui bbc', 'caribes anzoategui'],
        'busqueda_google': 'caribes de anzoategui beisbol venezuela'
    },
    'bravos': {
        'nombres': ['bravos de margarita', 'bravos de margarita bbc', 'bravos margarita'],
        'busqueda_google': 'bravos de margarita beisbol venezuela'
    },
    'cardenales': {
        'nombres': ['cardenales de lara', 'cardenales de lara bbc', 'cardenales lara'],
        'busqueda_google': 'cardenales de lara beisbol venezuela'
    },
    'navegantes': {
        'nombres': ['navegantes del magallanes', 'navegantes del magallanes bbc', 'navegantes magallanes'],
        'busqueda_google': 'navegantes del magallanes beisbol venezuela'
    },
    'leones': {
        'nombres': ['leones del caracas', 'leones del caracas bbc', 'leones caracas'],
        'busqueda_google': 'leones del caracas beisbol venezuela'
    }
}

# Páginas web oficiales de los equipos
PAGINAS = {
    'leones': 'https://leones.com/',
    'navegantes': 'https://magallanesbbc.com.ve/',
    'tiburones': 'https://www.tiburonesbbc.com/',
    'aguilas': 'https://aguilas.com/',
    'tigres': 'https://tigresdearaguabbc.com/',
    'caribes': 'https://caribesbbc.com/',
    'cardenales': 'https://cardenalesdelara.com/',
    'bravos': 'https://bravosdemargarita.com/'
}

# Canales de YouTube
YOUTUBE_CHANNELS = {
    'lvbp': 'UCxX1yG1yG1yG1yG1yG1yG1A',
    'espn': 'UCiWLfSweyRNmLpgEHekhoAg',
    'beisbolplay': 'UCbeisbolplay123456789',
}

def limpiar(txt):
    txt = re.sub(r'https?://\S+', '', txt)
    txt = re.sub(r'www\.\S+', '', txt)
    txt = re.sub(r'\s*-\s*(Meridiano\.net|MLB\.com|ESPN|Facebook)', '', txt, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', txt).strip()

def cargar_vistos():
    if os.path.exists(VISTOS_FILE):
        with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def guardar_visto(norm):
    with open(VISTOS_FILE, 'a', encoding='utf-8') as f:
        f.write(norm + '\n')

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
    """Detecta a qué equipo pertenece una noticia usando nombres completos."""
    t = titulo.lower()
    for eq, datos in EQUIPOS.items():
        # Buscar nombres completos primero (más específicos)
        for nombre in datos['nombres']:
            if nombre in t:
                return eq
    return 'general'

def obtener_youtube(canal_nombre, canal_id):
    """Obtiene videos recientes de un canal de YouTube."""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={canal_id}"
    videos = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
            entries = root.findall('atom:entry', ns)
            for entry in entries[:5]:
                video_id = entry.find('yt:videoId', ns).text
                titulo = entry.find('atom:title', ns).text
                link = entry.find('atom:link', ns).attrib['href']
                videos.append({
                    'id': f"yt_{video_id}",
                    'titulo': titulo,
                    'link': link,
                    'tipo': 'youtube'
                })
    except Exception as e:
        print(f"Error YouTube {canal_nombre}: {e}")
    return videos

def obtener_noticias_lvbp():
    """Obtiene noticias de LVBP.com."""
    noticias = []
    try:
        resp = requests.get('https://www.lvbp.com/noticias/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for art in soup.find_all(['article', 'div'], class_=re.compile('post|news', re.I))[:15]:
            tag = art.find(['h2', 'h3', 'a'])
            if tag:
                tit = limpiar(tag.get_text(strip=True))
                if len(tit) > 15:
                    desc = limpiar(art.find('p').get_text(strip=True)[:200]) if art.find('p') else ''
                    img = art.find('img')
                    img_url = urljoin('https://www.lvbp.com', img.get('src')) if img and img.get('src') else None
                    noticias.append({'titulo': tit, 'desc': desc, 'img': img_url, 'eq': detectar(tit), 'tipo': 'web'})
    except Exception as e:
        print(f"Error LVBP: {e}")
    return noticias

def obtener_noticias_google(equipo_key, datos_equipo):
    """Obtiene noticias de Google News usando el nombre completo del equipo."""
    noticias = []
    try:
        # Usar el nombre completo y específico para la búsqueda
        busqueda = datos_equipo['busqueda_google']
        url = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=VE&ceid=VE:es"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for item in soup.find_all('item')[:5]:
            tit = limpiar(item.find('title').get_text(strip=True))
            if len(tit) > 15:
                content = str(item.find('content')) if item.find('content') else ''
                img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
                img = img_match.group(1) if img_match else None
                desc = limpiar(BeautifulSoup(content, 'html.parser').get_text(strip=True)[:200])
                noticias.append({'titulo': tit, 'desc': desc, 'img': img, 'eq': equipo_key, 'tipo': 'web'})
    except Exception:
        pass
    return noticias

def obtener_noticias_pagina(equipo_key, url_base):
    """Obtiene noticias de la página web de un equipo."""
    noticias = []
    try:
        resp = requests.get(url_base, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for art in soup.find_all(['article', 'div'], class_=re.compile('post|news', re.I))[:10]:
            tag = art.find(['h2', 'h3', 'a'])
            if tag:
                tit = limpiar(tag.get_text(strip=True))
                if len(tit) > 15:
                    desc = limpiar(art.find('p').get_text(strip=True)[:200]) if art.find('p') else ''
                    img = art.find('img')
                    img_url = urljoin(url_base, img.get('src')) if img and img.get('src') else None
                    noticias.append({'titulo': tit, 'desc': desc, 'img': img_url, 'eq': equipo_key, 'tipo': 'web'})
    except Exception as e:
        print(f"Error {equipo_key}: {e}")
    return noticias

def obtener_jornada_hoy():
    """Obtiene los partidos de hoy desde calendario.json."""
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
    """Obtiene la tabla de posiciones de LVBP."""
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
    print("⚾ Iniciando bot LVBP completo...")
    vistos = cargar_vistos()
    todas_las_noticias = []
    
    # 1. Obtener noticias de LVBP.com
    print("📰 Buscando en LVBP.com...")
    todas_las_noticias.extend(obtener_noticias_lvbp())
    
    # 2. Obtener noticias de Google News para cada equipo (con nombres completos)
    print(" Buscando en Google News...")
    for eq, datos in EQUIPOS.items():
        print(f"  - Buscando: {datos['busqueda_google']}")
        todas_las_noticias.extend(obtener_noticias_google(eq, datos))
    
    # 3. Obtener noticias de páginas web de equipos
    print("🌐 Buscando en páginas de equipos...")
    for eq, url in PAGINAS.items():
        todas_las_noticias.extend(obtener_noticias_pagina(eq, url))
    
    # 4. Obtener videos de YouTube
    print("📺 Buscando en YouTube...")
    for canal_nombre, canal_id in YOUTUBE_CHANNELS.items():
        videos = obtener_youtube(canal_nombre, canal_id)
        for video in videos:
            todas_las_noticias.append({
                'titulo': video['titulo'],
                'desc': f"Ver video: {video['link']}",
                'img': None,
                'eq': detectar(video['titulo']),
                'tipo': 'youtube',
                'link': video['link']
            })
    
    # 5. Filtrar noticias nuevas (SIN LÍMITE)
    print(f" Total de noticias encontradas: {len(todas_las_noticias)}")
    finales = []
    for n in todas_las_noticias:
        norm = re.sub(r'[^a-z0-9]', '', n['titulo'].lower())
        if norm not in vistos and len(norm) > 15:
            vistos.add(norm)
            finales.append((norm, n))
    
    print(f"✅ Noticias nuevas a publicar: {len(finales)}")
    
    # 6. Publicar TODAS las noticias nuevas
    for norm, n in finales:
        logo = LOGOS.get(n['eq'], LOGOS['general'])
        
        if n['tipo'] == 'youtube':
            texto = f"📺 <b>{n['titulo']}</b>\n\n{n['desc']}"
        else:
            texto = f"⚾ <b>{n['titulo']}</b>\n\n{n['desc']}"
        
        if enviar_foto(n.get('img'), texto, logo):
            guardar_visto(norm)
            print(f"✅ Publicada: {n['titulo'][:40]}")
            time.sleep(2)
    
    # 7. Publicar jornada del día (si hay partidos hoy)
    print("📅 Verificando jornada de hoy...")
    jornada = obtener_jornada_hoy()
    if jornada:
        texto_jornada = f"📅 <b>{jornada.get('titulo', 'JORNADA DE HOY')}</b>\n\n{jornada.get('descripcion', 'Partidos de hoy')}"
        if enviar_foto(jornada.get('imagen'), texto_jornada, LOGOS['general']):
            print("📅 Jornada publicada")
            time.sleep(2)
    
    # 8. Publicar posiciones (cada 3 días)
    hoy_num = datetime.now().day
    if hoy_num % 3 == 0:
        print(" Obteniendo posiciones...")
        posiciones = obtener_posiciones()
        if posiciones:
            texto_pos = "🏆 <b>POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
            if enviar_mensaje(texto_pos):
                print("🏆 Posiciones publicadas")
                time.sleep(2)
    
    print("✅ Terminado")

if __name__ == '__main__':
    main()
