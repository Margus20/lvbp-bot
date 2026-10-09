import os, re, time, json, requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime

# ============ CONFIGURACIÓN ============
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBpalDia'
VISTOS_FILE = 'vistos.txt'
CALENDARIO_FILE = 'calendario.json'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ============ LOGOS DE CADA EQUIPO ============
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

# ============ DETECCIÓN DE EQUIPOS (nombres completos) ============
EQUIPOS = {
    'tiburones': ['tiburones de la guaira', 'tiburones lvg', 'tiburones de la guaira bbc'],
    'aguilas': ['aguilas del zulia', 'aguilas del zulia bbc', 'aguilas zulia'],
    'tigres': ['tigres de aragua', 'tigres de aragua bbc', 'tigres aragua'],
    'caribes': ['caribes de anzoategui', 'caribes de anzoategui bbc', 'caribes anzoategui'],
    'bravos': ['bravos de margarita', 'bravos de margarita bbc', 'bravos margarita'],
    'cardenales': ['cardenales de lara', 'cardenales de lara bbc', 'cardenales lara'],
    'navegantes': ['navegantes del magallanes', 'navegantes del magallanes bbc', 'navegantes magallanes'],
    'leones': ['leones del caracas', 'leones del caracas bbc', 'leones caracas']
}

# ============ 9 PÁGINAS WEB OFICIALES ============
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

# ============ 9 CANALES DE YOUTUBE ============
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

channel_id_cache = {}

# ============ FUNCIONES AUXILIARES ============
def limpiar(txt):
    return re.sub(r'\s+', ' ', re.sub(r'https?://\S+|www\.\S+', '', txt)).strip()

def cargar_vistos():
    if os.path.exists(VISTOS_FILE):
        with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def guardar_visto(norm):
    with open(VISTOS_FILE, 'a', encoding='utf-8') as f:
        f.write(norm + '\n')

def detectar_equipo(titulo):
    """Detecta el equipo usando nombres completos. Si no detecta, devuelve 'general'."""
    t = titulo.lower()
    for eq, nombres in EQUIPOS.items():
        for nombre in nombres:
            if nombre in t:
                return eq
    return 'general'

def obtener_channel_id(handle):
    if handle in channel_id_cache:
        return channel_id_cache[handle]
    try:
        resp = requests.get(f"https://www.youtube.com/{handle}", headers=HEADERS, timeout=10, allow_redirects=True)
        match = re.search(r'"channelId":"(UC[^"]+)"', resp.text)
        if match:
            cid = match.group(1)
            channel_id_cache[handle] = cid
            print(f"  ✅ {handle} -> {cid}")
            return cid
    except Exception as e:
        print(f"  ️ Error con {handle}: {e}")
    return None

# ============ ENVÍO A TELEGRAM (con lógica infalible de imágenes) ============
def enviar_foto(url_imagen, texto, logo_url):
    """Intenta con url_imagen. Si falla, usa logo_url (equipo o liga)."""
    # 1. Intentar imagen de la noticia
    try:
        if url_imagen and str(url_imagen).startswith('http'):
            resp = requests.get(url_imagen, headers=HEADERS, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 1000:
                files = {'photo': ('img.jpg', resp.content, 'image/jpeg')}
                data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
                r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', files=files, data=data, timeout=15)
                if r.status_code == 200:
                    return True
    except Exception:
        pass
    
    # 2. Respaldar con logo del equipo o de la liga
    try:
        resp = requests.get(logo_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            files = {'photo': ('logo.jpg', resp.content, 'image/jpeg')}
            data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
            r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', files=files, data=data, timeout=15)
            if r.status_code == 200:
                return True
    except Exception:
        pass
    return False

def enviar_mensaje(texto):
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data, timeout=10)
    return r.status_code == 200

# ============ FUENTES: PÁGINAS WEB (con enlace) ============
def obtener_noticias_web(equipo_key, url_base):
    noticias = []
    try:
        resp = requests.get(url_base, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
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
                        'titulo': tit, 'desc': desc, 'img': img_url, 'enlace': enlace,
                        'eq': detectar_equipo(tit), 'tipo': 'web'
                    })
    except Exception as e:
        print(f"  ⚠️ Error {equipo_key}: {e}")
    return noticias

# ============ FUENTES: YOUTUBE (con miniatura y enlace) ============
def obtener_videos_youtube(handle):
    videos = []
    cid = obtener_channel_id(handle)
    if not cid:
        return videos
    try:
        resp = requests.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}", timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}
            for entry in root.findall('atom:entry', ns)[:5]:
                video_id = entry.find('yt:videoId', ns).text
                titulo = entry.find('atom:title', ns).text
                link = entry.find('atom:link', ns).attrib['href']
                thumb = entry.find('media:group/media:thumbnail', ns)
                img = thumb.get('url') if thumb is not None else f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                videos.append({
                    'titulo': titulo, 'desc': 'Ver video completo en YouTube', 'img': img,
                    'enlace': link, 'eq': detectar_equipo(titulo), 'tipo': 'youtube'
                })
    except Exception as e:
        print(f"  ⚠️ Error YouTube {handle}: {e}")
    return videos

# ============ JORNADA Y POSICIONES ============
def obtener_jornada():
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with open(CALENDARIO_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for s in data.get('calendario', []):
            if s.get('fecha_inicio') <= hoy <= s.get('fecha_fin'):
                return s
        for s in data.get('calendario', []):
            if s.get('activo'):
                return s
    except Exception as e:
        print(f"  ️ Error calendario: {e}")
    return None

def obtener_posiciones():
    try:
        resp = requests.get('https://www.lvbp.com/posiciones/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tabla = soup.find('table', class_=re.compile('standings|tabla|posiciones', re.I))
        if tabla:
            pos = []
            for fila in tabla.find_all('tr')[1:6]:
                cols = fila.find_all('td')
                if len(cols) >= 3:
                    pos.append(f"{cols[1].get_text(strip=True)}: {cols[2].get_text(strip=True)}G-{cols[3].get_text(strip=True) if len(cols)>3 else '0'}P")
            return pos
    except Exception as e:
        print(f"  ⚠️ Error posiciones: {e}")
    return None

# ============ FUNCIÓN PRINCIPAL ============
def main():
    print("⚾ Iniciando bot LVBP...")
    vistos = cargar_vistos()
    todas = []
    
    # 1. Páginas web (9 fuentes)
    print("🌐 Páginas web...")
    for eq, url in PAGINAS.items():
        print(f"  - {eq}")
        todas.extend(obtener_noticias_web(eq, url))
    
    # 2. YouTube (9 canales)
    print("📺 YouTube...")
    for eq, handle in YOUTUBE_HANDLES.items():
        print(f"  - {eq}: {handle}")
        todas.extend(obtener_videos_youtube(handle))
    
    # 3. Filtrar nuevas (SIN LÍMITE)
    print(f"📊 Total: {len(todas)}")
    finales = []
    for n in todas:
        norm = re.sub(r'[^a-z0-9]', '', n['titulo'].lower())
        if norm not in vistos and len(norm) > 15:
            vistos.add(norm)
            finales.append((norm, n))
    
    print(f"✅ Nuevas: {len(finales)}")
    
    # 4. Publicar con lógica de imagen infalible
    for norm, n in finales:
        eq = n.get('eq', 'general')
        logo = LOGOS.get(eq, LOGOS['general'])
        img = n.get('img')
        if not img or not str(img).startswith('http'):
            img = logo
        
        if n['tipo'] == 'youtube':
            texto = f" <b>{n['titulo']}</b>\n\n{n['desc']}\n\n🔗 {n['enlace']}"
        else:
            texto = f"⚾ <b>{n['titulo']}</b>\n\n{n['desc']}\n\n🔗 {n['enlace']}"
        
        if enviar_foto(img, texto, logo):
            guardar_visto(norm)
            print(f"  ✅ {n['titulo'][:40]}")
            time.sleep(2)
        else:
            enviar_mensaje(texto)
            guardar_visto(norm)
            print(f"  ⚠️ Texto: {n['titulo'][:40]}")
            time.sleep(2)
    
    # 5. Jornada
    print(" Jornada...")
    j = obtener_jornada()
    if j:
        t = f"📅 <b>{j.get('titulo', 'JORNADA')}</b>\n\n{j.get('descripcion', '')}"
        if enviar_foto(j.get('imagen'), t, LOGOS['general']):
            print("  ✅ Jornada publicada")
            time.sleep(2)
    
    # 6. Posiciones (cada 3 días)
    if datetime.now().day % 3 == 0:
        print("🏆 Posiciones...")
        pos = obtener_posiciones()
        if pos:
            t = "🏆 <b>POSICIONES LVBP</b>\n\n" + "\n".join(pos)
            if enviar_mensaje(t):
                print("  ✅ Posiciones publicadas")
                time.sleep(2)
    
    print("✅ Terminado")

if __name__ == '__main__':
    main()
