import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

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

EQUIPOS_KEYWORDS = {
    'tiburones': ['tiburones', 'la guaira', 'guairistas'],
    'aguilas': ['aguilas', 'zulia'],
    'tigres': ['tigres', 'aragua'],
    'caribes': ['caribes', 'anzoategui', 'anzoátegui'],
    'bravos': ['bravos', 'margarita'],
    'cardenales': ['cardenales', 'lara'],
    'navegantes': ['navegantes', 'magallanes'],
    'leones': ['leones', 'caracas']
}

CALENDARIO_SEMANAS = {
    "2026-10-12": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg",
    "2026-10-19": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg",
    "2026-10-26": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
}

def limpiar_texto(texto):
    texto = re.sub(r'https?://\S+', '', texto)
    texto = re.sub(r'www\.\S+', '', texto)
    texto = re.sub(r'-\s*Meridiano\.net', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'-\s*\S+\.net', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'-\s*Facebook', '', texto, flags=re.IGNORECASE)
    texto = texto.strip()
    return texto

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        img_data = requests.get(url_img, headers=headers, timeout=15).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        r = requests.post(url, files=files, data=data, timeout=20)
        print("Foto enviada: " + str(r.status_code))
        return True
    except Exception as e:
        print("Error foto: " + str(e))
        return False

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    requests.post(url, data=data, timeout=15)

def detectar_equipo(titulo):
    titulo_lower = titulo.lower()
    equipos_encontrados = []
    for equipo, keywords in EQUIPOS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in titulo_lower:
                if equipo not in equipos_encontrados:
                    equipos_encontrados.append(equipo)
                break
    if len(equipos_encontrados) == 0 or len(equipos_encontrados) > 1:
        return 'general'
    return equipos_encontrados[0]

def obtener_noticias_por_equipo(equipo, keywords):
    print("Buscando noticias de " + equipo + "...")
    noticias = []
    keyword = keywords[0]
    rss_url = "https://news.google.com/rss/search?q=" + keyword + " béisbol&hl=es&gl=VE&ceid=VE:es"
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

# 1. LOGOS (Todos los equipos + General)
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

# 2. KEYWORDS (Exactas para evitar confusión con la MLB)
EQUIPOS_KEYWORDS = {
    'tiburones': ['tiburones de la guaira', 'tiburones'],
    'aguilas': ['aguilas del zulia', 'aguilas zulia'],
    'tigres': ['tigres de aragua', 'tigres aragua'],
    'caribes': ['caribes de anzoategui', 'caribes anzoategui'],
    'bravos': ['bravos de margarita', 'bravos margarita'],
    'cardenales': ['cardenales de lara', 'cardenales lara'],
    'navegantes': ['navegantes del magallanes', 'navegantes magallanes'],
    'leones': ['leones del caracas', 'leones caracas']
}

# 3. CALENDARIO
CALENDARIO_SEMANAS = {
    "2026-10-12": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
}

# --- FUNCIONES DE LIMPIEZA ---
def limpiar_texto(texto):
    # Elimina URLs completas
    texto = re.sub(r'https?://\S+', '', texto)
    texto = re.sub(r'www\.\S+', '', texto)
    # Elimina menciones de fuentes al final
    texto = re.sub(r'\s*[-–]\s*(Meridiano\.net|MLB\.com|ESPN|Facebook|Twitter|Instagram|Globovisión|Radiomiraflores|Líder en deportes)', '', texto, flags=re.IGNORECASE)
    # Elimina espacios dobles
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def normalizar(texto):
    return re.sub(r'[^a-z0-9]', '', texto.lower())

# --- FUNCIONES DE ENVÍO ---
def enviar_foto(url_img, texto, logo_respaldo):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Intentamos descargar la imagen original
    try:
        img_data = requests.get(url_img, headers=headers, timeout=10).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        r = requests.post(url, files=files, data=data, timeout=20)
        if r.status_code == 200:
            return True
    except:
        pass # Si falla, caemos al respaldo

    # Si la imagen original falló, enviamos el logo del equipo
    try:
        img_data = requests.get(logo_respaldo, headers=headers, timeout=10).content
        files = {'photo': ('logo.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        requests.post(url, files=files, data=data, timeout=20)
        return True
    except:
        return False

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    requests.post(url, data={'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=15)

# --- DETECCIÓN DE EQUIPO ---
def detectar_equipo(titulo):
    titulo_lower = titulo.lower()
    equipos_detectados = []
    for equipo, keywords in EQUIPOS_KEYWORDS.items():
        if any(kw in titulo_lower for kw in keywords):
            equipos_detectados.append(equipo)
    
    if len(equipos_detectados) == 1:
        return equipos_detectados[0]
    return 'general'

# --- FUENTE 1: LVBP.COM ---
def buscar_en_lvbp():
    print("📰 Buscando en LVBP.com...")
    noticias = []
    try:
        response = requests.get('https://www.lvbp.com/noticias/', timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        articulos = soup.find_all(['article', 'div'], class_=re.compile('post|article|news', re.I))
        for art in articulos[:10]:
            titulo_tag = art.find(['h2', 'h3', 'h4', 'a'])
            if titulo_tag:
                titulo = limpiar_texto(titulo_tag.get_text(strip=True))
                if len(titulo) > 15:
                    desc_tag = art.find('p')
                    desc = limpiar_texto(desc_tag.get_text(strip=True)[:200]) if desc_tag else ""
                    img_tag = art.find('img')
                    img = img_tag.get('src') if img_tag else None
                    if img and not img.startswith('http'):
                        img = 'https://www.lvbp.com' + img
                    noticias.append({'titulo': titulo, 'desc': desc, 'img': img})
    except Exception as e:
        print("Error LVBP: " + str(e))
    return noticias

# --- FUENTE 2: GOOGLE NEWS ---
def buscar_en_google():
    print("📰 Buscando en Google News...")
    noticias = []
    for equipo, keywords in EQUIPOS_KEYWORDS.items():
        try:
            query = keywords[0] + " beisbol"
            url = "https://news.google.com/rss/search?q=" + query + "&hl=es&gl=VE&ceid=VE:es"
            response = requests.get(url, timeout=15)
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
from urllib.parse import urljoin

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

# 1. LOGOS DE RESPALDO
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

# 2. URLs DE LOS EQUIPOS + KEYWORDS
EQUIPOS_INFO = {
    'leones': {'url': 'https://leones.com/', 'keywords': ['leones del caracas', 'leones caracas']},
    'navegantes': {'url': 'https://magallanesbbc.com.ve/', 'keywords': ['navegantes del magallanes', 'navegantes magallanes']},
    'tiburones': {'url': 'https://www.tiburonesbbc.com/noticias', 'keywords': ['tiburones de la guaira', 'tiburones']},
    'aguilas': {'url': 'https://aguilas.com/', 'keywords': ['aguilas del zulia', 'aguilas zulia']},
    'tigres': {'url': 'https://tigresdearaguabbc.com/', 'keywords': ['tigres de aragua', 'tigres aragua']},
    'caribes': {'url': 'https://caribesbbc.com/', 'keywords': ['caribes de anzoategui', 'caribes anzoategui']},
    'cardenales': {'url': 'https://cardenalesdelara.com/', 'keywords': ['cardenales de lara', 'cardenales lara']},
    'bravos': {'url': 'https://bravosdemargarita.com/', 'keywords': ['bravos de margarita', 'bravos margarita']}
}

# 3. CALENDARIO (Fecha ajustada a la semana actual para que se active)
CALENDARIO_SEMANAS = {
    "2026-10-05": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
}

# --- FUNCIONES DE LIMPIEZA EXTREMA ---
def limpiar_texto(texto):
    texto = re.sub(r'https?://\S+', '', texto)
    texto = re.sub(r'www\.\S+', '', texto)
    texto = re.sub(r'\s*[-–]\s*(Meridiano\.net|MLB\.com|ESPN|Facebook|Twitter|Instagram|Globovisión|Radiomiraflores|Líder en deportes|Leer más)', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def normalizar(texto):
    return re.sub(r'[^a-z0-9]', '', texto.lower())
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
from urllib.parse import urljoin

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

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

EQUIPOS_INFO = {
    'leones': {'url': 'https://leones.com/', 'keywords': ['leones del caracas', 'leones caracas']},
    'navegantes': {'url': 'https://magallanesbbc.com.ve/', 'keywords': ['navegantes del magallanes', 'navegantes magallanes']},
    'tiburones': {'url': 'https://www.tiburonesbbc.com/noticias', 'keywords': ['tiburones de la guaira', 'tiburones']},
    'aguilas': {'url': 'https://aguilas.com/', 'keywords': ['aguilas del zulia', 'aguilas zulia']},
    'tigres': {'url': 'https://tigresdearaguabbc.com/', 'keywords': ['tigres de aragua', 'tigres aragua']},
    'caribes': {'url': 'https://caribesbbc.com/', 'keywords': ['caribes de anzoategui', 'caribes anzoategui']},
    'cardenales': {'url': 'https://cardenalesdelara.com/', 'keywords': ['cardenales de lara', 'cardenales lara']},
    'bravos': {'url': 'https://bravosdemargarita.com/', 'keywords': ['bravos de margarita', 'bravos margarita']}
}

CALENDARIO_SEMANAS = {
    "2026-10-05": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
}

def limpiar_texto(texto):
    texto = re.sub(r'https?://\S+', '', texto)
    texto = re.sub(r'www\.\S+', '', texto)
    texto = re.sub(r'\s*[-–]\s*(Meridiano\.net|MLB\.com|ESPN|Facebook|Twitter|Instagram|Globovisión|Radiomiraflores|Líder en deportes|Leer más)', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def normalizar(texto):
    return re.sub(r'[^a-z0-9]', '', texto.lower())

def enviar_foto(url_img, texto, logo_respaldo):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Intento 1: Imagen original
    try:
        img_data = requests.get(url_img, headers=headers, timeout=10).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        r = requests.post(url, files=files, data=data, timeout=20)
        if r.status_code == 200:
            print("Foto original enviada")
            return True
    except Exception as e:
        print("Error imagen original: " + str(e))
    
    # Intento 2: Logo de respaldo
    try:
        img_data = requests.get(logo_respaldo, headers=headers, timeout=10).content
        files = {'photo': ('logo.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        requests.post(url, files=files, data=data, timeout=20)
        print("Logo de respaldo enviado")
        return True
    except Exception as e:
        print("Error logo respaldo: " + str(e))
        return False

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    requests.post(url, data={'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=15)

def detectar_equipo(titulo):
    titulo_lower = titulo.lower()
    for equipo, info in EQUIPOS_INFO.items():
        if any(kw in titulo_lower for kw in info['keywords']):
            return equipo
    return 'general'

def buscar_en_lvbp():
    print("📰 Fuente 1: LVBP.com")
    noticias = []
    try:
        response = requests.get('https://www.lvbp.com/noticias/', timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for art in soup.find_all(['article', 'div'], class_=re.compile('post|article|news', re.I))[:10]:
            titulo_tag = art.find(['h2', 'h3', 'h4', 'a'])
            if titulo_tag:
                titulo = limpiar_texto(titulo_tag.get_text(strip=True))
                if len(titulo) > 15:
                    desc_tag = art.find('p')
                    desc = limpiar_texto(desc_tag.get_text(strip=True)[:200]) if desc_tag else ""
                    img_tag = art.find('img')
                    img = img_tag.get('src') if img_tag else None
                    if img and not img.startswith('http'):
                        img = 'https://www.lvbp.com' + img
                    noticias.append({'titulo': titulo, 'desc': desc, 'img': img})
    except Exception as e:
        print("Error LVBP: " + str(e))
    return noticias

def buscar_en_google():
    print("📰 Fuente 2: Google News")
    noticias = []
    for equipo, info in EQUIPOS_INFO.items():
        try:
            query = info['keywords'][0] + " beisbol"
            url = "https://news.google.com/rss/search?q=" + query + "&hl=es&gl=VE&ceid=VE:es"
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('item')[:2]:
                titulo = item.find('title').get_text(strip=True) if item.find('title') else ""
                if len(titulo) > 15:
                    content = str(item.find('content')) if item.find('content') else ""
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
                    img = img_match.group(1) if img_match else None
                    desc = limpiar_texto(BeautifulSoup(content, 'html.parser').get_text(strip=True)[:200])
                    noticias.append({'titulo': limpiar_texto(titulo), 'desc': desc, 'img': img})
        except Exception as e:
            print("Error Google: " + str(e))
    return noticias

def buscar_en_equipos():
    print(" Fuente 3: Páginas de los 8 equipos")
    noticias = []
    for equipo, info in EQUIPOS_INFO.items():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(info['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            articulos = soup.find_all(['article', 'div'], class_=re.compile('post|article|news|card|entry', re.I))
            for art in articulos[:3]:
                titulo_tag = art.find(['h2', 'h3', 'h4', 'a'])
                if titulo_tag:
                    titulo = limpiar_texto(titulo_tag.get_text(strip=True))
                    if len(titulo) > 15:
                        desc_tag = art.find('p')
                        desc = limpiar_texto(desc_tag.get_text(strip=True)[:200]) if desc_tag else ""
                        img_tag = art.find('img')
                        img = img_tag.get('src') or img_tag.get('data-src') if img_tag else None
                        if img and not img.startswith('http'):
                            img = urljoin(info['url'], img)
                        noticias.append({'titulo': titulo, 'desc': desc, 'img': img})
        except Exception as e:
            print("Error en " + equipo + ": " + str(e))
    return noticias

def publicar_calendario():
    hoy = datetime.now().strftime('%Y-%m-%d')
    semana = None
    for fecha in sorted(CALENDARIO_SEMANAS.keys()):
        if fecha <= hoy:
            semana = fecha
    
    if semana:
        texto = "📅 <b>CALENDARIO LVBP - SEMANA DEL " + semana + "</b>\n\n🏟️ Todos los juegos de la semana\n\n⚾ Temporada 2026-2027"
        enviar_foto(CALENDARIO_SEMANAS[semana], texto, LOGOS['general'])
        print("📅 Calendario publicado")

def main():
    print(" Iniciando Mega Bot LVBP...")
    
    todas = buscar_en_lvbp() + buscar_en_google() + buscar_en_equipos()
    
    finales = []
    vistos = set()
    
    for n in todas:
        norm = normalizar(n['titulo'])
        if norm not in vistos and len(norm) > 15:
            vistos.add(norm)
            n['equipo'] = detectar_equipo(n['titulo'])
            finales.append(n)
            
            if len(finales) >= 20:
                break
                
    print("✅ Noticias únicas a publicar: " + str(len(finales)))
    
    for n in finales:
        equipo = n['equipo']
        logo = LOGOS.get(equipo, LOGOS['general'])
        texto = " <b>" + n['titulo'] + "</b>\n\n" + n['desc']
        
        if n['img']:
            enviar_foto(n['img'], texto, logo)
        else:
            enviar_foto(logo, texto, logo)
            
        print("Publicada: " + n['titulo'][:40])
        
    publicar_calendario()
    print("🏁 Proceso terminado.")

if __name__ == '__main__':
    main()

# --- FUNCIONES DE ENVÍO ---
def enviar_foto(url_img, texto, logo_respaldo):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # Intento 1: Imagen original de la fuente
    try:
        img_data = requests.get(url_img, headers=headers, timeout=10).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        r = requests.post(url, files=files, data=data, timeout=20)
        if r.status_code == 200:
            return True
    except:
        pass 
    
    # Intento 2: Logo de respaldo del equipo
    try:
        img_data = requests.get(logo_respaldo, headers=headers, timeout=10).content
        files = {'photo': ('logo.jpg', img_data, 'image/jpeg')}
        data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
        requests.post(url, files=files, data=data, timeout=20)
        return True
    except:
        return False

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    requests.post(url, data={'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=15)

# --- DETECCIÓN DE EQUIPO ---
def detectar_equipo(titulo):
    titulo_lower = titulo.lower()
    for equipo, info in EQUIPOS_INFO.items():
        if any(kw in titulo_lower for kw in info['keywords']):
            return equipo
    return 'general'

# --- FUENTE 1: LVBP.COM ---
def buscar_en_lvbp():
    print("📰 Fuente 1: LVBP.com")
    noticias = []
    try:
        response = requests.get('https://www.lvbp.com/noticias/', timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for art in soup.find_all(['article', 'div'], class_=re.compile('post|article|news', re.I))[:10]:
            titulo_tag = art.find(['h2', 'h3', 'h4', 'a'])
            if titulo_tag:
                titulo = limpiar_texto(titulo_tag.get_text(strip=True))
                if len(titulo) > 15:
                    desc_tag = art.find('p')
                    desc = limpiar_texto(desc_tag.get_text(strip=True)[:200]) if desc_tag else ""
                    img_tag = art.find('img')
                    img = img_tag.get('src') if img_tag else None
                    if img and not img.startswith('http'):
                        img = 'https://www.lvbp.com' + img
                    noticias.append({'titulo': titulo, 'desc': desc, 'img': img})
    except Exception as e:
        print("Error LVBP: " + str(e))
    return noticias

# --- FUENTE 2: GOOGLE NEWS ---
def buscar_en_google():
    print("📰 Fuente 2: Google News")
    noticias = []
    for equipo, info in EQUIPOS_INFO.items():
        try:
            query = info['keywords'][0] + " beisbol"
            url = "https://news.google.com/rss/search?q=" + query + "&hl=es&gl=VE&ceid=VE:es"
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('item')[:2]:
                titulo = item.find('title').get_text(strip=True) if item.find('title') else ""
                if len(titulo) > 15:
                    content = str(item.find('content')) if item.find('content') else ""
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
                    img = img_match.group(1) if img_match else None
                    desc = limpiar_texto(BeautifulSoup(content, 'html.parser').get_text(strip=True)[:200])
                    noticias.append({'titulo': limpiar_texto(titulo), 'desc': desc, 'img': img})
        except:
            continue
    return noticias

# --- FUENTE 3: PÁGINAS DE LOS 8 EQUIPOS ---
def buscar_en_equipos():
    print("📰 Fuente 3: Páginas de los 8 equipos")
    noticias = []
    for equipo, info in EQUIPOS_INFO.items():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(info['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos tarjetas de noticias genéricas en WordPress/sitios modernos
            articulos = soup.find_all(['article', 'div'], class_=re.compile('post|article|news|card|entry', re.I))
