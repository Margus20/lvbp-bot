import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

# LOGOS DE LOS 8 EQUIPOS + LVBP GENERAL
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

# PALABRAS CLAVE PARA DETECTAR CADA EQUIPO
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

# CALENDARIO SEMANAL (actualiza los links cada semana)
CALENDARIO_SEMANAS = {
    "2026-10-12": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg",
    "2026-10-19": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg",
    "2026-10-26": "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
}

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

def obtener_noticias_lvbp():
    print("Buscando noticias de todos los equipos...")
    noticias = []
    for equipo, keywords in EQUIPOS_KEYWORDS.items():
        keyword = keywords[0] + " LVBP"
        rss_url = "https://news.google.com/rss/search?q=" + keyword + "&hl=es&gl=VE&ceid=VE:es"
        try:
            response = requests.get(rss_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('item')
            for item in items[:2]:
                titulo = item.find('title').get_text(strip=True) if item.find('title') else None
                if titulo and len(titulo) > 10:
                    content = str(item.find('content')) if item.find('content') else ""
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
                    imagen = img_match.group(1) if img_match else None
                    descripcion = BeautifulSoup(content, 'html.parser').get_text(strip=True)[:300]
                    noticias.append({
                        'titulo': titulo,
                        'descripcion': descripcion,
                        'imagen_original': imagen,
                        'equipo_detectado': equipo
                    })
        except Exception as e:
            print("Error con " + equipo + ": " + str(e))
    return noticias[:6]

def publicar_calendario():
    print("Publicando calendario...")
    import datetime
    hoy = datetime.date.today().isoformat()
    semana_actual = None
    for fecha in sorted(CALENDARIO_SEMANAS.keys()):
        if fecha <= hoy:
            semana_actual = fecha
        else:
            break
    if semana_actual:
        link = CALENDARIO_SEMANAS[semana_actual]
        texto = "📅 <b>CALENDARIO LVBP - SEMANA DEL " + semana_actual + "</b>\n\n🏟️ Todos los juegos de la semana\n\n⚾ Temporada 2026-2027"
        enviar_foto(link, texto)
        print("Calendario publicado")
    else:
        print("No hay calendario para esta fecha")

def main():
    print("Iniciando bot LVBP...")
    noticias = obtener_noticias_lvbp()
    
    for noticia in noticias:
        equipo = detectar_equipo(noticia['titulo'])
        logo = LOGOS.get(equipo, LOGOS['general'])
        imagen_final = noticia['imagen_original'] if noticia['imagen_original'] else logo
        
        texto = "🦈 <b>" + noticia['titulo'] + "</b>\n\n" + noticia['descripcion']
        
        if not enviar_foto(imagen_final, texto):
            enviar_texto(texto)
        print("Publicada: " + noticia['titulo'][:50])
    
    publicar_calendario()
    print("Proceso terminado.")

if __name__ == '__main__':
    main()
