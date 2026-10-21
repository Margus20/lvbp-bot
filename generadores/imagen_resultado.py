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
    """Crea una imagen DINÁMICA y PROFESIONAL con el resultado del juego"""
    
    # 1. Crear canvas (900x500 pixels) - más grande para mejor calidad
    img = Image.new('RGBA', (900, 500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Crear fondo con gradiente (Azul oscuro LVBP)
    for y in range(500):
        # Gradiente de azul oscuro a negro
        r = int(20 + (0 - 20) * (y / 500))
        g = int(24 + (0 - 24) * (y / 500))
        b = int(82 + (40 - 82) * (y / 500))
        draw.line((0, y, 900, y), fill=(r, g, b, 255))
    
    # 3. Agregar borde dorado brillante
    draw.rectangle([0, 0, 899, 499], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, 891, 491], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes (las mismas que usas pero con tamaños ajustados)
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_marcador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_titulo = font_equipo = font_marcador = font_fecha = ImageFont.load_default()
    
    # 5. Título "RESULTADO FINAL" con efecto de sombra
    draw.text((452, 32), "⚾ RESULTADO FINAL", fill=(0, 0, 0, 180), font=font_titulo, anchor="mm")
    draw.text((450, 30), "⚾ RESULTADO FINAL", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # 6. Descargar logos
    logo_visitante = descargar_logo(detectar_equipo(visitante))
    logo_local = descargar_logo(detectar_equipo(local))
    
    # 7. Círculo decorativo detrás del marcador
    draw.ellipse([350, 140, 550, 340], fill=(0, 0, 0, 100))
    draw.ellipse([350, 140, 550, 340], outline=(255, 215, 0, 150), width=3)
    
    # 8. Equipo Visitante (Izquierda) - con sombra
    if logo_visitante:
        logo_visitante = logo_visitante.resize((150, 150), Image.Resampling.LANCZOS)
        # Crear sombra
        sombra = logo_visitante.copy()
        sombra = sombra.filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(sombra, (83, 163), sombra)
        img.paste(logo_visitante, (80, 160), logo_visitante)
    
    draw.text((155, 340), visitante[:12].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    # 9. Equipo Local (Derecha) - con sombra
    if logo_local:
        logo_local = logo_local.resize((150, 150), Image.Resampling.LANCZOS)
        sombra = logo_local.copy()
        sombra = sombra.filter(ImageFilter.GaussianBlur(radius=5))
        img.paste(sombra, (663, 163), sombra)
        img.paste(logo_local, (660, 160), logo_local)
    
    draw.text((745, 340), local[:12].upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="mm")
    
    # 10. Marcador CENTRAL (GRANDE, DORADO, con sombra 3D)
    marcador_text = f"{score_vis} - {score_loc}"
    draw.text((452, 252), marcador_text, fill=(0, 0, 0, 200), font=font_marcador, anchor="mm")
    draw.text((450, 250), marcador_text, fill=(255, 215, 0, 255), font=font_marcador, anchor="mm")
    
    # 11. Fecha con fondo redondeado semitransparente
    fecha_bg = draw.textbbox((200, 420, 700, 470), text=f"📅 {fecha}", font=font_fecha)
    draw.rounded_rectangle([200, 420, 700, 470], radius=15, fill=(0, 0, 0, 180))
    draw.text((450, 445), f"📅 {fecha}", fill=(255, 255, 255, 255), font=font_fecha, anchor="mm")
    
    # 12. Logo LVBP pequeño en esquina superior derecha
    logo_lvbp = descargar_logo('lvbp')
    if logo_lvbp:
        logo_lvbp = logo_lvbp.resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(logo_lvbp, (820, 10), logo_lvbp)
    
    # 13. Guardar en memoria (Bytes) para enviar a Telegram
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
