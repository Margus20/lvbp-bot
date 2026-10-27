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
    """Detecta qué equipo es para usar su logo"""
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
    """Crea una imagen VERTICAL de la tabla de posiciones (blindada contra errores)"""
    
    # 1. Canvas un poco más ancho (550x850) para dar aire a los nombres
    ancho = 550
    alto = 850
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Fondo con gradiente ROJO OSCURO a negro
    for y in range(alto):
        r = int(139 + (0 - 139) * (y / alto))
        g = int(0 + (0 - 0) * (y / alto))
        b = int(0 + (0 - 0) * (y / alto))
        draw.line((0, y, ancho, y), fill=(r, g, b, 255))
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, ancho-9, alto-9], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_registro = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_titulo = font_equipo = font_numero = font_registro = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo()
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título
    draw.text((ancho//2 + 1, 81), "🏆 TABLA DE POSICIONES", fill=(0, 0, 0, 150), font=font_titulo, anchor="mm")
    draw.text((ancho//2, 80), "🏆 TABLA DE POSICIONES", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # 7. Dibujar cada equipo (máximo 8)
    y_inicio = 140
    altura_fila = 75
    
    for i, equipo in enumerate(posiciones[:8]):
        nombre = str(equipo.get('nombre', 'Equipo'))
        
        # Acortar nombres de forma segura
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
        # Truncar a 18 caracteres máximo para evitar solapamiento a toda costa
        nombre_corto = nombre_corto[:18].upper()
        
        jg = str(equipo.get('jg', 0))
        jp = str(equipo.get('jp', 0))
        racha = str(equipo.get('racha', ''))
        
        # Determinar emoji de racha
        emoji_racha = "🟢" if "G" in racha else "🔴" if "P" in racha else "⚪"
        
        # Color de fondo según posición
        if i == 0:
            color_fila = (180, 50, 50, 220)  # 1ro
        elif i < 4:
            color_fila = (130, 20, 20, 200)  # Playoffs
        else:
            color_fila = (90, 10, 10, 180)   # Resto
        
        y = y_inicio + (i * altura_fila)
        
        # Fondo de la fila redondeado
        draw.rounded_rectangle([20, y, ancho-20, y + 65], radius=12, fill=color_fila)
        
        # --- DISEÑO DE LA FILA ---
        equipo_key = detectar_equipo(nombre)
        url_logo = LOGOS_EQUIPOS.get(equipo_key, LOGO_CANAL)
        logo_equipo = descargar_logo(url_logo)
        
        if logo_equipo:
            logo_equipo = logo_equipo.resize((45, 45), Image.Resampling.LANCZOS)
            img.paste(logo_equipo, (25, y + 10), logo_equipo)
            
            # Número de posición (círculo dorado)
            draw.ellipse([78, y + 18, 108, y + 48], fill=(255, 215, 0, 255))
            draw.text((93, y + 33), str(i + 1), fill=(0, 0, 0, 255), font=font_numero, anchor="mm")
            
            # Nombre del equipo (con sombra para resaltar)
            draw.text((116, y + 34), nombre_corto, fill=(0, 0, 0, 150), font=font_equipo, anchor="lm")
            draw.text((115, y + 33), nombre_corto, fill=(255, 255, 255, 255), font=font_equipo, anchor="lm")
        
        # Récord (JG-JP) + Emoji de racha (Alineado a la derecha)
        record_text = f"{jg}-{jp} {emoji_racha}"
        draw.text((ancho - 30, y + 33), record_text, fill=(255, 215, 0, 255), font=font_registro, anchor="rm")
    
    # 8. Footer
    draw.rounded_rectangle([80, alto-60, ancho-80, alto-20], radius=15, fill=(0, 0, 0, 200))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 9. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
