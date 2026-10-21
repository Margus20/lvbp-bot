# generadores/imagen_resultado.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

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

def crear_imagen_resultado(visitante, local, score_vis, score_loc, fecha):
    """Crea una imagen dinámica con el resultado del juego"""
    
    # 1. Crear canvas (800x400 pixels) con fondo azul oscuro LVBP
    img = Image.new('RGBA', (800, 400), (20, 24, 82, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Cargar fuentes (DejaVu viene preinstalado en Ubuntu/GitHub Actions)
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_marcador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_titulo = font_equipo = font_marcador = font_fecha = ImageFont.load_default()
    
    # 3. Dibujar Título
    draw.text((400, 40), "⚾ RESULTADO FINAL", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # 4. Descargar y dibujar logos
    logo_visitante = descargar_logo(detectar_equipo(visitante))
    logo_local = descargar_logo(detectar_equipo(local))
    
    # Equipo Visitante (Izquierda)
    if logo_visitante:
        logo_visitante = logo_visitante.resize((120, 120), Image.Resampling.LANCZOS)
        img.paste(logo_visitante, (100, 100), logo_visitante)
    draw.text((160, 260), visitante[:15].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    # Equipo Local (Derecha)
    if logo_local:
        logo_local = logo_local.resize((120, 120), Image.Resampling.LANCZOS)
        img.paste(logo_local, (580, 100), logo_local)
    draw.text((640, 260), local[:15].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    # 5. Marcador central (GRANDE y DORADO)
    marcador_text = f"{score_vis} - {score_loc}"
    draw.text((400, 160), marcador_text, fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
    
    # 6. Fecha y detalles
    draw.text((400, 340), f"📅 {fecha}", fill=(200, 200, 200, 255), font=font_fecha, anchor="mm")
    
    # 7. Guardar en memoria (Bytes) para enviar a Telegram
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
