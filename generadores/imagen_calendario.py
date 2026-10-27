# generadores/imagen_calendario.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime

# URL del logo del canal y de los equipos
LOGO_CANAL = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/logo_pag.png'
LOGOS_EQUIPOS = {
    'magallanes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/magallanes.png',
    'cardenales': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/cardenales.png',
    'tigres': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/tigres.png',
    'aguilas': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/aguilas.png',
    'leones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/leones.png',
    'tiburones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/tiburones.png',
    'bravos': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/bravos.png',
    'caribes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/caribes.png',
}

# Colores exactos de cada equipo (RGB) - Basados en tu página
COLORES_EQUIPOS = {
    'cardenales': (220, 38, 38),        # Rojo Cardenales
    'caribes': (245, 245, 245),         # Blanco/Gray Caribes
    'tigres': (0, 38, 92),              # Azul oscuro Tigres
    'bravos': (78, 173, 173),           # Turquesa Bravos
    'leones': (0, 32, 96),              # Azul marino Leones
    'aguilas': (249, 97, 0),            # Naranja Águilas
    'tiburones': (41, 41, 249),         # Azul eléctrico Tiburones
    'magallanes': (91, 183, 230),       # Azul claro Magallanes
}

def descargar_logo(url):
    """Descarga una imagen desde una URL"""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

def detectar_equipo(nombre):
    """Detecta qué equipo es para usar su logo y color"""
    nombre_lower = nombre.lower()
    equipos = {
        'magallanes': ['magallanes', 'navegantes'],
        'cardenales': ['cardenales'],
        'tigres': ['tigres', 'aragua'],
        'aguilas': ['aguilas', 'zulia'],
        'leones': ['leones', 'caracas'],
        'tiburones': ['tiburones', 'guaira'],
        'bravos': ['bravos', 'margarita'],
        'caribes': ['caribes', 'anzoategui'],
    }
    for equipo, nombres in equipos.items():
        if any(n in nombre_lower for n in nombres):
            return equipo
    return 'magallanes'

def crear_imagen_calendario(juegos, fecha_hoy=None):
    """
    Crea una imagen VERTICAL de la jornada del día con tarjetas 
    divididas por colores de equipo, exactamente como en la página web.
    """
    
    # 1. Canvas VERTICAL más grande (600x1100) para tarjetas profesionales
    ancho = 600
    alto = 1100
    img = Image.new('RGBA', (ancho, alto), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Si no hay fecha, usar la de hoy
    if not fecha_hoy:
        fecha_hoy = datetime.now().strftime('%d de %B').capitalize()
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_hora = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_estadio = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_fecha = font_equipo = font_hora = font_estadio = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo(LOGO_CANAL)
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título "JORNADA DEL DÍA" centrado arriba
    draw.text((ancho//2 + 1, 81), "📅 JORNADA DEL DÍA", fill=(0, 0, 0, 150), font=font_titulo, anchor="mm")
    draw.text((ancho//2, 80), " JORNADA DEL DÍA", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # 7. Fecha debajo del título
    draw.text((ancho//2, 125), fecha_hoy, fill=(220, 38, 38), font=font_fecha, anchor="mm")
    
    # 8. Línea separadora dorada
    draw.line([(50, 155), (ancho-50, 155)], fill=(255, 215, 0, 255), width=3)
    
    # 9. Dibujar cada juego como tarjeta individual
    y_inicio = 180
    altura_tarjeta = 200  # Más alta para que quepan logos grandes
    espacio_entre = 20
    
    for i, juego in enumerate(juegos[:4]):  # Máximo 4 tarjetas para que quepan bien
        visitante = juego.get('visitante', '???')
        local = juego.get('local', '???')
        hora = juego.get('hora', 'Por definir')
        transmision = juego.get('transmision', '')
        lugar = juego.get('lugar', '')
        
        y = y_inicio + (i * (altura_tarjeta + espacio_entre))
        
        # Obtener colores de los equipos
        color_visitante = COLORES_EQUIPOS.get(detectar_equipo(visitante), (150, 150, 150))
        color_local = COLORES_EQUIPOS.get(detectar_equipo(local), (150, 150, 150))
        
        # Tarjeta con bordes redondeados y sombra
        draw.rectangle([20, y, ancho-20, y + altura_tarjeta], fill=(255, 255, 255, 255))
        draw.rectangle([20, y, ancho-20, y + altura_tarjeta], outline=(255, 215, 0, 200), width=2)
        
        # Mitad izquierda (Visitante) - Color del equipo
        draw.rectangle([25, y + 5, ancho//2 - 5, y + 130], fill=color_visitante)
        
        # Mitad derecha (Local) - Color del equipo
        draw.rectangle([ancho//2 + 5, y + 5, ancho-25, y + 130], fill=color_local)
        
        # Línea divisoria dorada en el medio
        draw.line([(ancho//2, y + 5), (ancho//2, y + 130)], fill=(255, 215, 0, 255), width=3)
        
        # Descargar y pegar logo visitante (grande, 80x80)
        url_logo_vis = LOGOS_EQUIPOS.get(detectar_equipo(visitante), LOGO_CANAL)
        logo_visitante = descargar_logo(url_logo_vis)
        if logo_visitante:
            logo_visitante = logo_visitante.resize((80, 80), Image.Resampling.LANCZOS)
            img.paste(logo_visitante, (ancho//4 - 40, y + 25), logo_visitante)
        
        # Descargar y pegar logo local (grande, 80x80)
        url_logo_loc = LOGOS_EQUIPOS.get(detectar_equipo(local), LOGO_CANAL)
        logo_local = descargar_logo(url_logo_loc)
        if logo_local:
            logo_local = logo_local.resize((80, 80), Image.Resampling.LANCZOS)
            img.paste(logo_local, (3*ancho//4 - 40, y + 25), logo_local)
        
        # Nombres de equipos (blancos con sombra)
        draw.text((ancho//4, y + 115), visitante.upper(), fill=(0, 0, 0, 180), font=font_equipo, anchor="mm")
        draw.text((ancho//4, y + 113), visitante.upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
        
        draw.text((3*ancho//4, y + 115), local.upper(), fill=(0, 0, 0, 180), font=font_equipo, anchor="mm")
        draw.text((3*ancho//4, y + 113), local.upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
        
        # Círculo VS en el centro
        draw.ellipse([ancho//2 - 30, y + 55, ancho//2 + 30, y + 115], fill=(255, 255, 255, 255))
        draw.ellipse([ancho//2 - 30, y + 55, ancho//2 + 30, y + 115], outline=(255, 215, 0, 255), width=3)
        draw.text((ancho//2, y + 85), "VS", fill=(220, 38, 38), font=font_equipo, anchor="mm")
        
        # Franja inferior negra con hora y estadio
        draw.rectangle([25, y + 135, ancho-25, y + altura_tarjeta - 5], fill=(20, 20, 20, 255))
        draw.rectangle([25, y + 135, ancho-25, y + altura_tarjeta - 5], outline=(255, 215, 0, 100), width=1)
        
        # Hora (con ícono de reloj)
        draw.text((35, y + 155), f"🕐 {hora}", fill=(255, 215, 0, 255), font=font_hora, anchor="lm")
        
        # Estadio
        if lugar:
            draw.text((ancho//2, y + 155), f"🏟️ {lugar}", fill=(255, 255, 255, 255), font=font_estadio, anchor="mm")
        
        # Transmisión (abajo a la derecha)
        if transmision and transmision != 'Por definir':
            draw.text((ancho - 35, y + 155), f"📺 {transmision}", fill=(255, 215, 0, 255), font=font_estadio, anchor="rm")
    
    # 10. Footer con información
    draw.rectangle([50, alto-70, ancho-50, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-45), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 11. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
