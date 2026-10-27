# generadores/imagen_resultado.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from datetime import datetime

# URLs de los logos desde tu repositorio lvbp-stats
LOGOS = {
    'magallanes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/magallanes.png',
    'cardenales': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/cardenales.png',
    'tigres': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/tigres.png',
    'aguilas': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/aguilas.png',
    'leones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/leones.png',
    'tiburones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/tiburones.png',
    'bravos': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/bravos.png',
    'caribes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/caribes.png',
    'lvbp': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/logo_pag.png',
}

def detectar_equipo(nombre):
    """Detecta qué equipo es para usar su logo"""
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
    return 'lvbp'

def descargar_logo(equipo_key):
    """Descarga el logo desde URL y lo devuelve como imagen PIL"""
    url = LOGOS.get(equipo_key, LOGOS['lvbp'])
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

def crear_imagen_resultados(juegos, fecha_hoy=None):
    """
    Crea una imagen VERTICAL que contiene TODOS los resultados del día 
    en filas HORIZONTALES (Visitante a la izquierda, Local a la derecha).
    """
    
    # 1. Canvas vertical un poco más alto (600x900) para que quepan hasta 4 juegos holgadamente
    ancho = 600
    alto = 900
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Fondo con gradiente Azul Oscuro LVBP (El que te gusta)
    for y in range(alto):
        r = int(20 + (0 - 20) * (y / alto))
        g = int(24 + (0 - 24) * (y / alto))
        b = int(82 + (40 - 82) * (y / alto))
        draw.line((0, y, ancho, y), fill=(r, g, b, 255))
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, ancho-9, alto-9], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_marcador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_titulo = font_fecha = font_equipo = font_marcador = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo('lvbp')
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título y Fecha
    draw.text((ancho//2, 80), "⚾ RESULTADOS DEL DÍA", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    if not fecha_hoy:
        fecha_hoy = datetime.now().strftime('%d de %B de %Y').capitalize()
    draw.text((ancho//2, 115), fecha_hoy, fill=(255, 255, 255, 200), font=font_fecha, anchor="mm")
    
    # Línea separadora dorada
    draw.line([(50, 135), (ancho-50, 135)], fill=(255, 215, 0, 255), width=2)
    
    # 7. Dibujar cada juego en una fila HORIZONTAL
    y_inicio = 160
    altura_fila = 120  # Altura de cada tarjeta de juego
    
    for i, juego in enumerate(juegos[:4]): # Máximo 4 juegos para que se vea perfecto
        visitante = juego.get('visitante', '???')
        local = juego.get('local', '???')
        score_vis = str(juego.get('scoreVisitante', '0'))
        score_loc = str(juego.get('scoreLocal', '0'))
        
        y = y_inicio + (i * (altura_fila + 15)) # +15 de espacio entre filas
        
        # Fondo de la fila (azul muy oscuro semitransparente para resaltar)
        draw.rounded_rectangle([20, y, ancho-20, y + altura_fila], radius=15, fill=(10, 15, 50, 180))
        draw.rounded_rectangle([20, y, ancho-20, y + altura_fila], radius=15, outline=(255, 215, 0, 100), width=1)
        
        # --- LADO IZQUIERDO: VISITANTE ---
        logo_vis = descargar_logo(detectar_equipo(visitante))
        if logo_vis:
            logo_vis = logo_vis.resize((60, 60), Image.Resampling.LANCZOS)
            img.paste(logo_vis, (35, y + 30), logo_vis)
        
        # Nombre visitante (recortado a 16 caracteres para evitar solapamiento)
        nombre_vis = visitante[:16].upper()
        draw.text((105, y + 40), nombre_vis, fill=(255, 255, 255, 255), font=font_equipo, anchor="lm")
        draw.text((140, y + 75), score_vis, fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
        
        # --- CENTRO: SEPARADOR ---
        draw.text((ancho//2, y + 75), "-", fill=(255, 255, 255, 150), font=font_marcador, anchor="mm")
        
        # --- LADO DERECHO: LOCAL ---
        draw.text((ancho-140, y + 75), score_loc, fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
        
        nombre_loc = local[:16].upper()
        draw.text((ancho-105, y + 40), nombre_loc, fill=(255, 255, 255, 255), font=font_equipo, anchor="rm")
        
        logo_loc = descargar_logo(detectar_equipo(local))
        if logo_loc:
            logo_loc = logo_loc.resize((60, 60), Image.Resampling.LANCZOS)
            img.paste(logo_loc, (ancho-95, y + 30), logo_loc)
            
    # 8. Footer con información
    draw.rounded_rectangle([100, alto-70, ancho-100, alto-20], radius=15, fill=(0, 0, 0, 150))
    draw.text((ancho//2, alto-45), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 9. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
