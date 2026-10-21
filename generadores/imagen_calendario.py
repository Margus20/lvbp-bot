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
    return 'magallanes' # Fallback por defecto

def crear_imagen_calendario(juegos, fecha_hoy=None):
    """Crea una imagen VERTICAL de la jornada del día con fondo blanco y logos"""
    
    # 1. Crear canvas VERTICAL (500x800 pixels)
    img = Image.new('RGBA', (500, 800), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Si no hay fecha, usar la de hoy
    if not fecha_hoy:
        fecha_hoy = datetime.now().strftime('%d de %B').capitalize()
    
    # 3. Agregar borde dorado brillante
    draw.rectangle([0, 0, 499, 799], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, 491, 791], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_hora = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_detalle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_fecha = font_hora = font_equipo = font_detalle = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo(LOGO_CANAL)
    if logo_canal:
        logo_canal = logo_canal.resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título "JORNADA DEL DÍA" centrado arriba
    draw.text((252, 102), "📅 JORNADA DEL DÍA", fill=(0, 0, 0, 100), font=font_titulo, anchor="mm")
    draw.text((250, 100), "📅 JORNADA DEL DÍA", fill=(20, 24, 82, 255), font=font_titulo, anchor="mm")
    
    # 7. Fecha debajo del título
    draw.text((250, 145), fecha_hoy, fill=(139, 0, 0, 255), font=font_fecha, anchor="mm")
    
    # 8. Línea separadora dorada
    draw.line([(50, 175), (450, 175)], fill=(255, 215, 0, 255), width=3)
    
    # 9. Dibujar cada juego (máximo 5 para que quepan bien)
    y_inicio = 200
    altura_juego = 110
    
    for i, juego in enumerate(juegos[:5]):
        visitante = juego.get('visitante', '???')
        local = juego.get('local', '???')
        hora = juego.get('hora', 'Por definir')
        transmision = juego.get('transmision', '')
        lugar = juego.get('lugar', '')
        
        y = y_inicio + (i * altura_juego)
        
        # Fondo del juego (gris muy claro con borde)
        draw.rounded_rectangle([20, y, 480, y + 95], radius=10, fill=(245, 245, 245, 255))
        draw.rounded_rectangle([20, y, 480, y + 95], radius=10, outline=(200, 200, 200, 255), width=2)
        
        # Línea roja decorativa a la izquierda
        draw.rounded_rectangle([20, y, 28, y + 95], radius=5, fill=(211, 47, 47, 255))
        
        # Hora (arriba a la izquierda, en azul)
        draw.text((40, y + 20), f"🕐 {hora}", fill=(20, 24, 82, 255), font=font_hora, anchor="lm")
        
        # 🆕 Descargar y pegar logos de los equipos (tamaño 35x35)
        url_logo_vis = LOGOS_EQUIPOS.get(detectar_equipo(visitante), LOGO_CANAL)
        logo_visitante = descargar_logo(url_logo_vis)
        if logo_visitante:
            logo_visitante = logo_visitante.resize((35, 35), Image.Resampling.LANCZOS)
            img.paste(logo_visitante, (130, y + 8), logo_visitante)
            
        url_logo_loc = LOGOS_EQUIPOS.get(detectar_equipo(local), LOGO_CANAL)
        logo_local = descargar_logo(url_logo_loc)
        if logo_local:
            logo_local = logo_local.resize((35, 35), Image.Resampling.LANCZOS)
            img.paste(logo_local, (330, y + 8), logo_local)
        
        # Equipos (centro, ajustado un poco hacia abajo para no tapar los logos)
        equipos_texto = f"{visitante} vs {local}"
        draw.text((250, y + 50), equipos_texto, fill=(0, 0, 0, 255), font=font_equipo, anchor="mm")
        
        # Detalles (estadio y transmisión)
        detalles = []
        if lugar:
            detalles.append(f"🏟️ {lugar}")
        if transmision and transmision != 'Por definir':
            detalles.append(f"📺 {transmision}")
        
        if detalles:
            detalles_texto = " | ".join(detalles)
            draw.text((250, y + 78), detalles_texto, fill=(100, 100, 100, 255), font=font_detalle, anchor="mm")
    
    # 10. Footer con información
    draw.rounded_rectangle([50, 730, 450, 780], radius=15, fill=(20, 24, 82, 255))
    draw.text((250, 755), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_detalle, anchor="mm")
    
    # 11. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
