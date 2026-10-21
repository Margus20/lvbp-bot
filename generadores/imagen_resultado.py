# generadores/imagen_resultado.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
    """Crea una imagen VERTICAL con el logo del canal y el local abajo"""
    
    # 1. Crear canvas VERTICAL (500x800 pixels)
    img = Image.new('RGBA', (500, 800), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Crear fondo con gradiente (Azul oscuro LVBP) - Ajustado a 800 de alto
    for y in range(800):
        r = int(20 + (0 - 20) * (y / 800))
        g = int(24 + (0 - 24) * (y / 800))
        b = int(82 + (40 - 82) * (y / 800))
        draw.line((0, y, 500, y), fill=(r, g, b, 255))
    
    # 3. Agregar borde dorado brillante - Ajustado a 500x800
    draw.rectangle([0, 0, 499, 799], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, 491, 791], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_marcador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_titulo = font_equipo = font_marcador = font_fecha = ImageFont.load_default()
    
    # 5. 🆕 LOGO DEL CANAL en la esquina superior izquierda
    logo_canal = descargar_logo('lvbp')
    if logo_canal:
        logo_canal = logo_canal.resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título "RESULTADO FINAL" centrado arriba
    draw.text((250, 100), "⚾ RESULTADO FINAL", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # 7. Descargar logos de los equipos
    logo_visitante = descargar_logo(detectar_equipo(visitante))
    logo_local = descargar_logo(detectar_equipo(local))
    
    # 8. Equipo VISITANTE (Parte SUPERIOR) - con sombra
    if logo_visitante:
        logo_visitante = logo_visitante.resize((140, 140), Image.Resampling.LANCZOS)
        sombra_vis = logo_visitante.copy().filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(sombra_vis, (183, 163), sombra_vis)
        img.paste(logo_visitante, (180, 160), logo_visitante)
    
    draw.text((250, 320), visitante[:15].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    # 9. Marcador en el CENTRO (Visitante arriba, Local abajo)
    draw.text((250, 410), str(score_vis), fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
    draw.text((250, 480), "-", fill=(255, 255, 255, 200), font=font_marcador, anchor="mm")
    draw.text((250, 550), str(score_loc), fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
    
    # 10. Equipo LOCAL (Parte INFERIOR) - con sombra
    draw.text((250, 640), local[:15].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    if logo_local:
        logo_local = logo_local.resize((140, 140), Image.Resampling.LANCZOS)
        sombra_loc = logo_local.copy().filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(sombra_loc, (183, 683), sombra_loc)
        img.paste(logo_local, (180, 680), logo_local)
    
    # 11. Fecha con fondo redondeado semitransparente (abajo del todo)
    draw.rounded_rectangle([100, 730, 400, 780], radius=15, fill=(0, 0, 0, 180))
    draw.text((250, 755), f"📅 {fecha}", fill=(255, 255, 255, 255), font=font_fecha, anchor="mm")
    
    # 12. Guardar en memoria (Bytes) para enviar a Telegram
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
