import os
import json
import time
import requests
from datetime import datetime
import json5

# ============================================
# CONFIGURACIÓN
# ============================================
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPalDia'

DATA_JS_URL = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/js/data.js'
TU_PAGINA = 'https://margus20.github.io/lvbp-stats/'

VISTOS_FILE = 'vistos.json'

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

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def cargar_vistos():
    """Carga el historial de lo ya publicado."""
    if os.path.exists(VISTOS_FILE):
        with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'noticias': [], 'resultados': '', 'posiciones': '', 'calendario': ''}

def guardar_vistos(datos):
    """Guarda el historial."""
    with open(VISTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def obtener_data_js():
    """Descarga y parsea el archivo data.js usando json5."""
    print("📡 Descargando data.js de tu página...")
    try:
        resp = requests.get(DATA_JS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        # json5 lee JavaScript nativo (con comentarios, sin comillas, etc.)
        datos = json5.loads(resp.text)
        
        print("✅ Datos extraídos exitosamente con json5")
        print(f"   - {len(datos.get('noticias', []))} noticias")
        print(f"   - {len(datos.get('resultados', []))} resultados")
        print(f"   - {len(datos.get('posiciones', []))} equipos en posiciones")
        print(f"   - {len(datos.get('calendario', []))} juegos en calendario")
        return datos
        
    except Exception as e:
        print(f"⚠️ Error al descargar data.js: {e}")
        return None

def detectar_equipo(texto):
    """Detecta qué equipo se menciona para usar su logo."""
    texto_lower = texto.lower()
    equipos = {
        'tiburones': ['tiburones', 'la guaira'],
        'aguilas': ['aguilas', 'zulia'],
        'tigres': ['tigres', 'aragua'],
        'caribes': ['caribes', 'anzoategui'],
        'bravos': ['bravos', 'margarita'],
        'cardenales': ['cardenales', 'lara'],
        'navegantes': ['navegantes', 'magallanes'],
        'leones': ['leones', 'caracas']
    }
    for equipo, nombres in equipos.items():
        if any(nombre in texto_lower for nombre in nombres):
            return equipo
    return 'general'

def enviar_con_imagen(texto, imagen_url, logo_key='general'):
    """Envía mensaje a Telegram con imagen."""
    logo_url = LOGOS.get(logo_key, LOGOS['general'])
    
    # Intentar enviar con la imagen de la noticia
    if imagen_url and imagen_url.startswith('http'):
        try:
            resp = requests.get(imagen_url, headers=HEADERS, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 1000:
                files = {'photo': ('noticia.jpg', resp.content, 'image/jpeg')}
                data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
                r = requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
                    files=files, data=data, timeout=15
                )
                if r.status_code == 200:
                    return True
        except:
            pass
    
    # Fallback: enviar con el logo del equipo
    try:
        resp = requests.get(logo_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            files = {'photo': ('logo.jpg', resp.content, 'image/jpeg')}
            data = {'chat_id': CHANNEL, 'caption': texto, 'parse_mode': 'HTML'}
            r = requests.post(
                f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
                files=files, data=data, timeout=15
            )
            return r.status_code == 200
    except:
        pass
    
    # Último recurso: solo texto
    data = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data, timeout=10)
    return True

# ============================================
# FUNCIONES DE PUBLICACIÓN
# ============================================

def publicar_noticias(datos, vistos):
    """Publica noticias nuevas con imagen, título y enlace."""
    print("📰 Publicando noticias...")
    
    for noticia in datos.get('noticias', []):
        titulo = noticia.get('titulo', '')
        norm = titulo.lower().strip()
        
        # Verificar si ya se publicó
        if norm in [v.lower().strip() for v in vistos['noticias']]:
            continue
        
        # Construir mensaje
        tag = noticia.get('tag', 'LVBP')
        fecha = noticia.get('fecha', '')
        resumen = noticia.get('resumen', '')
        imagen = noticia.get('imagen', '')
        
        texto = (
            f"📰 <b>{titulo}</b>\n\n"
            f"🏷️ {tag}\n"
            f"📅 {fecha}\n\n"
            f"{resumen[:200]}\n\n"
            f"🔗 Leer más: {TU_PAGINA}"
        )
        
        logo_key = detectar_equipo(titulo)
        
        if enviar_con_imagen(texto, imagen, logo_key):
            print(f"  ✅ Publicada: {titulo[:50]}")
            vistos['noticias'].append(titulo)
            time.sleep(2)
        else:
            print(f"  ️ Error al publicar: {titulo[:50]}")

def publicar_resultados(datos, vistos):
    """Publica resultados si cambiaron."""
    print("⚾ Publicando resultados...")
    
    resultados = datos.get('resultados', [])
    if not resultados:
        return
    
    texto = " <b>RESULTADOS</b>\n\n"
    for r in resultados:
        visitante = r.get('visitante', '')
        local = r.get('local', '')
        score_vis = r.get('scoreVisitante', 0)
        score_loc = r.get('scoreLocal', 0)
        fecha = r.get('fecha', '')
        texto += f"{visitante} {score_vis} - {score_loc} {local} ({fecha})\n"
    
    texto += f"\n🔗 Ver más: {TU_PAGINA}#resultados"
    
    if texto != vistos.get('resultados'):
        if enviar_con_imagen(texto, None, 'general'):
            print("  ✅ Resultados publicados")
            vistos['resultados'] = texto
            time.sleep(2)
    else:
        print("  ⏭️ Sin cambios en resultados")

def publicar_posiciones(datos, vistos):
    """Publica tabla de posiciones si cambió."""
    print(" Publicando posiciones...")
    
    posiciones = datos.get('posiciones', [])
    if not posiciones:
        return
    
    texto = "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n"
    for i, eq in enumerate(posiciones, 1):
        nombre = eq.get('nombre', '').replace(' de Anzoátegui', '').replace(' de Aragua', '').replace(' de Lara', '').replace(' de Margarita', '').replace(' del Zulia', '').replace(' de La Guaira', '').replace(' del Caracas', '').replace(' del Magallanes', '')
        jg = eq.get('jg', 0)
        jp = eq.get('jp', 0)
        texto += f"{i}. {nombre} ({jg}-{jp})\n"
    
    texto += f"\n🔗 Ver completa: {TU_PAGINA}#posiciones"
    
    if texto != vistos.get('posiciones'):
        if enviar_con_imagen(texto, None, 'general'):
            print("  ✅ Posiciones publicadas")
            vistos['posiciones'] = texto
            time.sleep(2)
    else:
        print("  ⏭️ Sin cambios en posiciones")

def publicar_calendario(datos, vistos):
    """Publica jornada del día."""
    print(" Publicando calendario...")
    
    calendario = datos.get('calendario', [])
    if not calendario:
        return
    
    hoy = datetime.now().strftime('%d %b')
    texto = f"📅 <b>JORNADA DE HOY - {hoy}</b>\n\n"
    
    for juego in calendario:
        visitante = juego.get('visitante', '')
        local = juego.get('local', '')
        hora = juego.get('hora', 'Por definir')
        transmision = juego.get('transmision', '')
        
        texto += f" {hora} - {visitante} vs {local}\n"
        if transmision and transmision != 'Por definir':
            texto += f"    {transmision}\n"
    
    texto += f"\n🔗 Ver calendario: {TU_PAGINA}#calendario"
    
    if texto != vistos.get('calendario'):
        if enviar_con_imagen(texto, None, 'general'):
            print("  ✅ Calendario publicado")
            vistos['calendario'] = texto
            time.sleep(2)
    else:
        print("  ⏭️ Sin cambios en calendario")

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    print(" Bot LVBP - Extrayendo de TU PÁGINA WEB")
    print(f" Fuente: {DATA_JS_URL}")
    print(f"🌐 Página: {TU_PAGINA}")
    print("=" * 50)
    
    # Cargar historial
    vistos = cargar_vistos()
    
    # Obtener datos de tu página
    datos = obtener_data_js()
    
    if not datos:
        print("❌ No se pudieron obtener los datos")
        return
    
    # Publicar novedades
    publicar_noticias(datos, vistos)
    publicar_resultados(datos, vistos)
    publicar_posiciones(datos, vistos)
    publicar_calendario(datos, vistos)
    
    # Guardar historial actualizado
    guardar_vistos(vistos)
    
    print("=" * 50)
    print("✅ Bot completado")

if __name__ == '__main__':
    main()
