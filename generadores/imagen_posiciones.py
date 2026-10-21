# generadores/imagen_posiciones.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO

# URL del logo del canal
LOGO_CANAL = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/logo_pag.png'

def descargar_logo():
    """Descarga el logo del canal"""
    try:
        resp = requests.get(LOGO_CANAL, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

def crear_imagen_posiciones(posiciones):
    """Crea una imagen VERTICAL de la tabla de posiciones con fondo rojo oscuro"""
    
    # 1. Crear canvas VERTICAL (500x800 pixels)
    img = Image.new('RGBA', (500, 800), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Crear fondo con gradiente ROJO OSCURO
    for y in range(800):
        # Gradiente de rojo oscuro a negro
        r = int(139 + (0 - 139) * (y / 800))
        g = int(0 + (0 - 0) * (y / 800))
        b = int(0 + (0 - 0) * (y / 800))
        draw.line((0, y, 500, y), fill=(r, g, b, 255))
    
    # 3. Agregar borde dorado brillante
    draw.rectangle([0, 0, 499, 799], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, 491, 791], outline=(255, 215, 0, 150), width=2)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_registro = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_titulo = font_equipo = font_numero = font_registro = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo()
    if logo_canal:
        logo_canal = logo_canal.resize((60, 60), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título "TABLA DE POSICIONES" centrado arriba
    draw.text((250, 100), "🏆 TABLA DE POSICIONES", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # 7. Dibujar cada equipo (máximo 8)
    y_inicio = 160
    altura_fila = 70
    
    for i, equipo in enumerate(posiciones[:8]):
        nombre = equipo.get('nombre', '???')
        # Acortar nombres largos
        nombre_corto = (nombre
            .replace(' de Anzoátegui', '')
            .replace(' de Aragua', '')
            .replace(' de Lara', '')
            .replace(' de Margarita', '')
            .replace(' del Zulia', '')
            .replace(' de La Guaira', '')
            .replace(' del Caracas', '')
            .replace(' del Magallanes', ''))
        
        jj = equipo.get('jj', 0)
        jg = equipo.get('jg', 0)
        jp = equipo.get('jp', 0)
        racha = equipo.get('racha', '')
        
        # Color de fondo según posición (1ro = dorado, 2-4 = rojo claro, resto = rojo oscuro)
        if i == 0:
            color_fila = (180, 50, 50, 200)  # Dorado-rojo (1ro)
        elif i < 4:
            color_fila = (120, 20, 20, 180)  # Rojo claro (playoffs)
        else:
            color_fila = (100, 10, 10, 150)  # Rojo oscuro
        
        y = y_inicio + (i * altura_fila)
        
        # Fondo de la fila
        draw.rounded_rectangle([20, y, 480, y + 60], radius=10, fill=color_fila)
        
        # Número de posición (círculo dorado)
        draw.ellipse([30, y + 10, 60, y + 40], fill=(255, 215, 0, 255))
        draw.text((45, y + 25), str(i + 1), fill=(0, 0, 0, 255), font=font_numero, anchor="mm")
        
        # Nombre del equipo
        draw.text((80, y + 25), nombre_corto.upper(), fill=(255, 255, 255, 255), font=font_equipo, anchor="lm")
        
        # Récord (JG-JP)
        record_text = f"{jg}-{jp}"
        draw.text((460, y + 25), record_text, fill=(255, 215, 0, 255), font=font_registro, anchor="rm")
    
    # 8. Footer con información
    draw.rounded_rectangle([50, 730, 450, 780], radius=15, fill=(0, 0, 0, 180))
    draw.text((250, 755), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_registro, anchor="mm")
    
    # 9. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
