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
            contenido = soup.get_text()
            if 'resultado' in contenido.lower() or 'marcador' in contenido.lower():
                enviar_texto("🦈 <b>TIBURONES - RESULTADOS</b>\n\n Revisando últimos resultados...\n\nPróximamente: Información actualizada de juegos.")
                return True
                
    except Exception as e:
        print(f" Error buscando resultados: {e}")
    
    return False

def obtener_calendario_tiburones():
    """Busca calendario de juegos de Tiburones"""
    print("🦈 Buscando calendario de Tiburones...")
    
    try:
        response = requests.get('https://www.tiburonesbbc.com/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar secciones de calendario
        calendario = []
        
        # Buscar tablas o listas de juegos
        tablas = soup.find_all('table')
        for tabla in tablas[:2]:
            filas = tabla.find_all('tr')
            for fila in filas[:5]:
                celdas = fila.find_all(['td', 'th'])
                texto = ' '.join([c.get_text(strip=True) for c in celdas[:4]])
                if texto and ('Tibur' in texto or len(texto) > 10):
                    calendario.append(texto)
        
        if calendario:
            texto = " <b>CALENDARIO TIBURONES</b>\n\n"
            texto += '\n'.join(calendario[:5])
            enviar_texto(texto)
            return True
        else:
            enviar_texto("🦈 <b>CALENDARIO TIBURONES</b>\n\n📅 Próximamente: Calendario de juegos actualizado.\n\n Temporada 2026-2027")
            return True
            
    except Exception as e:
        print(f" Error buscando calendario: {e}")
    
    return False

def main():
    print(f"🤖 Bot Tiburones - {datetime.now()}")
    print("=" * 50)
    
    total = 0
    
    # 1. Noticias
    noticias = obtener_noticias_tiburones()
    total += noticias
    
    # 2. Resultados
    if obtener_resultados_tiburones():
        total += 1
    
    # 3. Calendario
    if obtener_calendario_tiburones():
        total += 1
    
    if total == 0:
        enviar_texto("🦈 <b>TIBURONES DE LA GUAIRA</b>\n\n⚾ Información próximamente disponible.\n\n🔔 Activa notificaciones para no perderte nada.")
    
    print(f"✅ Completado. Publicaciones: {total}")
    print("=" * 50)

if __name__ == '__main__':
    main()
