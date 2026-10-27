# generadores/imagen_posiciones.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

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

# Colores exactos de cada equipo (RGB)
COLORES_EQUIPOS = {
    'cardenales': (220, 38, 38),      # Rojo Cardenales
    'caribes': (245, 245, 245),       # Blanco/Gray Caribes
    'tigres': (0, 38, 92),            # Azul oscuro Tigres
    'bravos': (78, 173, 173),         # Turquesa Bravos
    'leones': (0, 32, 96),            # Azul marino Leones
    'aguilas': (249, 97, 0),          # Naranja Águilas
    'tiburones': (41, 41, 249),       # Azul eléctrico Tiburones
    'magallanes': (91, 183, 230),     # Azul claro Magallanes
}

def descargar_logo(url=LOGO_CANAL):
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
    nombre_lower = str(nombre).lower()
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

def crear_imagen_posiciones(posiciones):
    """
    Crea una imagen VERTICAL de la tabla de posiciones 
    con los colores exactos de cada equipo y todas las columnas estadísticas.
    """
    
    # 1. Canvas más grande para acomodar todas las columnas (650x950)
    ancho = 650
    alto = 950
    img = Image.new('RGBA', (ancho, alto), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Fondo blanco
    draw.rectangle([0, 0, ancho, alto], fill=(255, 255, 255, 255))
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_stats = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_header = font_equipo = font_numero = font_stats = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo()
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título
    draw.text((ancho//2 + 1, 81), "🏆 TABLA DE POSICIONES LVBP", fill=(0, 0, 0, 150), font=font_titulo, anchor="mm")
    draw.text((ancho//2, 80), " TABLA DE POSICIONES LVBP", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # 7. Header de columnas (fondo dorado)
    y_header = 130
    draw.rectangle([20, y_header, ancho-20, y_header + 40], fill=(255, 215, 0, 255))
    
    # Columnas del header
    columnas = ["#", "EQUIPO", "JJ", "JG", "JP", "PCT", "DIF", "RACHA"]
    x_positions = [40, 110, 270, 330, 390, 460, 530, 590]
    
    for i, col in enumerate(columnas):
        draw.text((x_positions[i], y_header + 20), col, fill=(0, 0, 0, 255), font=font_header, anchor="mm")
    
    # Línea separadora
    draw.line([(20, y_header + 40), (ancho-20, y_header + 40)], fill=(255, 215, 0, 255), width=2)
    
    # 8. Dibujar cada equipo (máximo 8)
    y_inicio = 180
    altura_fila = 65
    
    for i, equipo in enumerate(posiciones[:8]):
        nombre = str(equipo.get('nombre', 'Equipo'))
        equipo_key = detectar_equipo(nombre)
        
        # Obtener color del equipo
        color_equipo = COLORES_EQUIPOS.get(equipo_key, (100, 100, 100))
        
        # Acortar nombres
        nombre_corto = (nombre
            .replace(' de Anzoátegui', '')
            .replace(' de Aragua', '')
            .replace(' de Lara', '')
            .replace(' de Margarita', '')
            .replace(' del Zulia', '')
            .replace(' de La Guaira', '')
            .replace(' del Caracas', '')
            .replace(' del Magallanes', '')
        )
        nombre_corto = nombre_corto[:16].upper()
        
        # Obtener estadísticas
        jj = str(equipo.get('jj', 0))
        jg = str(equipo.get('jg', 0))
        jp = str(equipo.get('jp', 0))
        pct = str(equipo.get('pct', '.000'))
        dif = str(equipo.get('dif', '0.0'))
        racha = str(equipo.get('racha', ''))
        
        y = y_inicio + (i * altura_fila)
        
        # Fondo de la fila con el color del equipo
        draw.rectangle([20, y, ancho-20, y + 60], fill=color_equipo)
        
        # Borde inferior blanco para separar filas
        draw.line([(20, y + 60), (ancho-20, y + 60)], fill=(255, 255, 255, 100), width=1)
        
        # Número de posición (círculo blanco con número)
        draw.ellipse([28, y + 10, 58, y + 40], fill=(255, 255, 255, 255))
        draw.text((43, y + 25), str(i + 1), fill=(0, 0, 0, 255), font=font_numero, anchor="mm")
        
        # Logo del equipo
        url_logo = LOGOS_EQUIPOS.get(equipo_key, LOGO_CANAL)
        logo_equipo = descargar_logo(url_logo)
        if logo_equipo:
            logo_equipo = logo_equipo.resize((35, 35), Image.Resampling.LANCZOS)
            img.paste(logo_equipo, (70, y + 12), logo_equipo)
        
        # Nombre del equipo (texto blanco con sombra negra)
        draw.text((115, y + 31), nombre_corto, fill=(0, 0, 0, 180), font=font_equipo, anchor="lm")
        draw.text((113, y + 30), nombre_corto, fill=(255, 255, 255, 255), font=font_equipo, anchor="lm")
        
        # Estadísticas (texto blanco centrado en cada columna)
        # JJ
        draw.text((x_positions[2], y + 30), jj, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
        # JG
        draw.text((x_positions[3], y + 30), jg, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
        # JP
        draw.text((x_positions[4], y + 30), jp, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
        # PCT
        draw.text((x_positions[5], y + 30), pct, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
        # DIF
        draw.text((x_positions[6], y + 30), dif, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
        # RACHA
        draw.text((x_positions[7], y + 30), racha, fill=(255, 255, 255, 255), font=font_stats, anchor="mm")
    
    # 9. Footer
    draw.rectangle([20, alto-60, ancho-20, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 10. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
