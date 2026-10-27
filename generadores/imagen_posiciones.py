# generadores/imagen_posiciones.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random

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

# 🆕 Colores EXACTOS extraídos de tu archivo equipos.js (Hex a RGB)
COLORES_EQUIPOS = {
    'cardenales': (217, 13, 30),      # #D90D1E - Rojo Cardenales
    'caribes': (242, 242, 242),       # #F2F2F2 - Blanco/Gray Caribes
    'tigres': (4, 41, 89),            # #042959 - Azul oscuro Tigres
    'bravos': (86, 166, 166),         # #56A6A6 - Turquesa Bravos
    'leones': (8, 32, 64),            # #082040 - Azul marino Leones
    'aguilas': (242, 70, 7),          # #F24607 - Naranja exacto Águilas ✅
    'tiburones': (33, 4, 217),        # #2104D9 - Azul eléctrico Tiburones
    'magallanes': (91, 169, 217),     # #5BA9D9 - Azul claro Magallanes
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

# Función para dibujar la textura de pelotas
def dibujar_pelota_béisbol(draw, x, y, radio):
    """Dibuja una pelota de béisbol sutil en el fondo"""
    draw.ellipse([x-radio, y-radio, x+radio, y+radio], fill=(255, 255, 255, 255))
    draw.arc([x-radio+3, y-radio+3, x+radio-3, y+radio-3], start=45, end=135, fill=(220, 38, 38, 80), width=2)
    draw.arc([x-radio+3, y-radio+3, x+radio-3, y+radio-3], start=225, end=315, fill=(220, 38, 38, 80), width=2)

def crear_imagen_posiciones(posiciones):
    """
    Crea una imagen VERTICAL de la tabla de posiciones centrada, 
    con textura de fondo, colores exactos de la web y textos limpios.
    """
    
    # 1. Canvas (650x1000)
    ancho = 650
    alto = 1000
    # Fondo gris intermedio suave
    img = Image.new('RGBA', (ancho, alto), (230, 230, 230, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Textura de fondo (75 pelotas - 5 veces más)
    random.seed(42)
    for _ in range(75):
        px = random.randint(40, ancho-40)
        py = random.randint(140, alto-80)
        pr = random.randint(12, 28)
        dibujar_pelota_béisbol(draw, px, py, pr)
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_stats = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_header = font_equipo = font_numero = font_stats = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo()
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título SIN emoji y SIN sombra duplicada
    draw.text((ancho//2, 60), "TABLA DE POSICIONES LVBP", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # 7. Header de columnas PEGADO al primer equipo
    y_header = 100
    altura_header = 40
    draw.rectangle([20, y_header, ancho-20, y_header + altura_header], fill=(255, 215, 0, 255))
    
    # Columnas del header
    columnas = ["#", "EQUIPO", "JJ", "JG", "JP", "PCT", "DIF", "RACHA"]
    x_positions = [40, 110, 270, 330, 390, 460, 530, 590]
    
    for i, col in enumerate(columnas):
        draw.text((x_positions[i], y_header + 20), col, fill=(0, 0, 0, 255), font=font_header, anchor="mm")
    
    # Línea separadora
    draw.line([(20, y_header + altura_header), (ancho-20, y_header + altura_header)], fill=(255, 215, 0, 255), width=2)
    
    # 8. CÁLCULO DE CENTRADO VERTICAL
    num_equipos = len(posiciones[:8])
    altura_fila = 65
    altura_total_filas = num_equipos * altura_fila
    
    # Espacio disponible (desde justo debajo del header hasta arriba del footer)
    y_top = y_header + altura_header  # Justo debajo del header, sin espacio
    y_bottom = alto - 60
    espacio_disponible = y_bottom - y_top
    
    # Calcular Y inicial para centrar el bloque de filas
    y_inicio = y_top + ((espacio_disponible - altura_total_filas) // 2)
    
    # 9. Dibujar cada equipo (máximo 8)
    for i, equipo in enumerate(posiciones[:8]):
        nombre = str(equipo.get('nombre', 'Equipo'))
        equipo_key = detectar_equipo(nombre)
        
        # Obtener color exacto del equipo
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
        
        # Fondo de la fila con el color exacto del equipo
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
        
        # DETECTAR si el fondo es claro (Caribes: 242+242+242 = 726 / 3 = 242 > 200)
        es_fondo_claro = sum(color_equipo) / 3 > 200
        color_texto = (0, 0, 0) if es_fondo_claro else (255, 255, 255)
        
        # Nombre del equipo: SIN sombra, solo texto puro y limpio
        draw.text((115, y + 28), nombre_corto, fill=color_texto, font=font_equipo, anchor="lm")
        
        # Estadísticas en negrita y con el color de contraste correcto
        draw.text((x_positions[2], y + 28), jj, fill=color_texto, font=font_stats, anchor="mm")
        draw.text((x_positions[3], y + 28), jg, fill=color_texto, font=font_stats, anchor="mm")
        draw.text((x_positions[4], y + 28), jp, fill=color_texto, font=font_stats, anchor="mm")
        draw.text((x_positions[5], y + 28), pct, fill=color_texto, font=font_stats, anchor="mm")
        draw.text((x_positions[6], y + 28), dif, fill=color_texto, font=font_stats, anchor="mm")
        draw.text((x_positions[7], y + 28), racha, fill=color_texto, font=font_stats, anchor="mm")
    
    # 10. Footer
    draw.rectangle([20, alto-60, ancho-20, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 11. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
