import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
LOGO = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

RSS_URL = "https://news.google.com/rss/search?q=%22Tiburones+de+La+Guaira%22&hl=es&gl=VE&ceid=VE:es"

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_data = requests.get(url_img, headers=headers, timeout=15).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {
            'chat_id': CHANNEL,
            'caption': texto,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        r = requests.post(url, files=files, data=data, timeout=20)
        print("✅ Foto enviada: " + str(r.status_code))
    except Exception as e:
        print("❌ Error foto: " + str(e))
        enviar_texto(texto)

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    requests.post(url, data=data, timeout=15)

def extraer_imagen_de_url(url_noticia):
    """Va a la página original y extrae la imagen principal"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_noticia, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar imagen principal de varias formas
        img = None
        
        # 1. Buscar Open Graph image (la más común)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img = og_image.get('content')
        
        # 2. Buscar Twitter card image
        if not img:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                img = twitter_image.get('content')
        
        # 3. Buscar primera imagen grande en el contenido
        if not img:
            images = soup.find_all('img')
            for image in images:
                src = image.get('src') or image.get('data-src')
                if src and 'logo' not in src.lower() and len(src) > 30:
                    img = src
                    break
        
        return img
        
    except Exception as e:
        print("Error extrayendo imagen: " + str(e))
        return None

def obtener_noticias_google():
    print("Obteniendo noticias de Google News...")
    noticias = []
    
    try:
        response = requests.get(RSS_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('item')
        
        for item in items[:3]:
            titulo_tag = item.find('title')
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
            
            link_tag = item.find('link')
            url_noticia = link_tag.get_text(strip=True) if link_tag else None
            
            # Extraer imagen del contenido RSS
            content_tag = item.find('content')
            imagen_url = None
            descripcion = ""
            
            if content_tag:
                contenido = str(content_tag)
                
                # Método 1: Buscar en etiqueta img
                img_match = re.search(r'<img[^>]+src="([^">]+)"', contenido)
                if img_match:
                    imagen_url = img_match.group(1)
                
                # Método 2: Buscar en enclosure
                if not imagen_url:
                    enclosure = item.find('enclosure')
                    if enclosure and enclosure.get('type', '').startswith('image'):
                        imagen_url = enclosure.get('url')
                
                # Extraer texto
                descripcion = BeautifulSoup(contenido, 'html.parser').get_text(strip=True)[:300]
            
            # Si no hay imagen del RSS, intentar ir a la página original
            if not imagen_url and url_noticia:
                print("Buscando imagen en: " + url_noticia[:50] + "...")
                imagen_url = extraer_imagen_de_url(url_noticia)
            
            if titulo and len(titulo) > 10:
                noticias.append({
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'imagen': imagen_url,
                    'url': url_noticia
                })
        
        print("Noticias encontradas: " + str(len(noticias)))
        
    except Exception as e:
        print("Error RSS: " + str(e))
    
    return noticias

def main():
    print("Iniciando bot...")
    
    # 1. Obtener y publicar noticias
    noticias = obtener_noticias_google()
    
    for i, noticia in enumerate(noticias):
        titulo = noticia['titulo']
        descripcion = noticia['descripcion']
        imagen = noticia['imagen']
        
        texto = "🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n<b>" + titulo + "</b>"
        if descripcion:
            texto += "\n\n" + descripcion
        
        if imagen:
            print("🖼️ Usando imagen original: " + imagen[:60] + "...")
            enviar_foto(imagen, texto)
        else:
            print("⚠️ Sin imagen, usando logo")
            enviar_foto(LOGO, texto)
        
        print("Publicada noticia " + str(i+1))
    
    # 2. Publicar Calendario
    link_cal = "https://i.postimg.cc/FKjfcHxV/1791385375160-11zon.jpg"
    texto_cal = "📅 <b>CALENDARIO LVBP - SEMANA 1</b>\n\n🏟️ Todos los juegos del 12-16 de octubre\n\n Temporada 2026-2027"
    enviar_foto(link_cal, texto_cal)
    
    print("✅ Proceso terminado.")

if __name__ == '__main__':
    main()import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'
LOGO = "https://i.postimg.cc/J7Hm024y/image-search-1791382706892.png"

RSS_URL = "https://news.google.com/rss/search?q=%22Tiburones+de+La+Guaira%22&hl=es&gl=VE&ceid=VE:es"

def enviar_foto(url_img, texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'
    try:
        img_data = requests.get(url_img, timeout=10).content
        files = {'photo': ('img.jpg', img_data, 'image/jpeg')}
        data = {
            'chat_id': CHANNEL,
            'caption': texto,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        r = requests.post(url, files=files, data=data, timeout=20)
        print("Foto enviada: " + str(r.status_code))
    except Exception as e:
        print("Error foto: " + str(e))
        enviar_texto(texto)

def enviar_texto(texto):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    requests.post(url, data=data, timeout=15)

def obtener_noticias_google():
    print("Obteniendo noticias de Google News...")
    noticias = []
    
    try:
        response = requests.get(RSS_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('item')
        
        for item in items[:3]:
    print("Proceso terminado.")

if __name__ == '__main__':
    main()
