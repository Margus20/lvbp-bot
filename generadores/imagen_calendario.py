# generadores/imagen_calendario.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime
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

# Colores exactos de cada equipo (RGB) - Basados en tu página
COLORES_EQUIPOS = {
    'cardenales': (220, 38, 38),        # Rojo Cardenales
    'caribes': (245, 245, 245),         # Blanco/Gray Caribes
    'tigres': (0, 38, 92),              # Azul oscuro Tigres
    'bravos': (78, 173, 173),           # Turquesa Bravos
    'leones': (0, 32, 96),              # Azul marino Leones
    'aguilas': (249, 97, 0),            # Naranja Águilas ✅ CORREGIDO
    'tiburones': (41, 41, 249),         # Azul eléctrico Tiburones
    'magallanes': (91, 183, 230),       # Azul claro Magallanes
}

# Logos de televisoras con URLs CORRECTAS (basadas en canales.js)
LOGOS_TV = {
    'meridiano': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/meridianotv.png',
    'meridiano tv': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/meridianotv.png',
    'bym': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/bymtv.png',
    'bym sport': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/bymtv.png',
    'baseball': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/baseballtv.png',
    'tves': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/tves.png',
}

# 🆕 Diccionario para traducir meses al español
MESES_ES = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
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
    divididas por colores de equipo, centradas y con textura de fondo.
    """
    
    # 1. Canvas VERTICAL (600x1100)
    ancho = 600
    alto = 1100
    # 🆕 Cambio 1: Fondo gris suave en lugar de blanco
    img = Image.new('RGBA', (ancho, alto), (230, 230, 230, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. Si no hay fecha, usar la de hoy y TRADUCIR al español
    if not fecha_hoy:
        fecha_en = datetime.now().strftime('%d de %B').capitalize()
        # Traducir mes de inglés a español
        for mes_en, mes_es in MESES_ES.items():
            fecha_en = fecha_en.replace(mes_en, mes_es)
        fecha_hoy = fecha_en
    
    # 3. Textura de fondo (pelotas de béisbol)
    random.seed(42)
    # 🆕 Cambio 2: 5 veces más pelotas (75 en lugar de 15)
    for _ in range(75):
        px = random.randint(40, ancho-40)
        py = random.randint(140, alto-80)
        pr = random.randint(12, 28)
        # Círculo blanco (pelota)
        draw.ellipse([px-pr, py-pr, px+pr, py+pr], fill=(255, 255, 255, 255))
        # Costuras rojas tenues
        draw.arc([px-pr+3, py-pr+3, px+pr-3, py+pr-3], start=45, end=135, fill=(220, 38, 38, 80), width=2)
        draw.arc([px-pr+3, py-pr+3, px+pr-3, py+pr-3], start=225, end=315, fill=(220, 38, 38, 80), width=2)
    
    # 4. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # 5. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_hora = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_estadio = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_fecha = font_equipo = font_hora = font_estadio = font_footer = ImageFont.load_default()
    
    # 6. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo(LOGO_CANAL)
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 7. Título SIN emoji
    draw.text((ancho//2, 70), "JORNADA DEL DÍA", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # 8. Fecha debajo del título (ya traducida)
    draw.text((ancho//2, 105), fecha_hoy, fill=(220, 38, 38), font=font_fecha, anchor="mm")
    
    # 9. Línea separadora dorada
    draw.line([(50, 135), (ancho-50, 135)], fill=(255, 215, 0, 255), width=3)
    
    # 10. CÁLCULO DE CENTRADO VERTICAL (para 1, 2, 3 o 4 juegos)
    num_juegos = min(len(juegos), 4)
    altura_tarjeta = 200
    espacio_entre = 20
    altura_total_tarjetas = (num_juegos * altura_tarjeta) + ((num_juegos - 1) * espacio_entre)
    
    # Espacio disponible (restando ~160px del header y ~80px del footer)
    espacio_disponible = alto - 160 - 80
    y_inicio = 160 + ((espacio_disponible - altura_total_tarjetas) // 2)
    
    # 11. Dibujar cada juego como tarjeta individual
    for i, juego in enumerate(juegos[:4]):
        visitante = juego.get('visitante', '???')
        local = juego.get('local', '???')
        hora = juego.get('hora', 'Por definir')
        transmision = juego.get('transmision', '')
        lugar = juego.get('lugar', '')
        
        y = y_inicio + (i * (altura_tarjeta + espacio_entre))
        
        # Obtener colores de los equipos
        color_visitante = COLORES_EQUIPOS.get(detectar_equipo(visitante), (150, 150, 150))
        color_local = COLORES_EQUIPOS.get(detectar_equipo(local), (150, 150, 150))
        
        # Tarjeta con bordes redondeados (fondo blanco tapa la textura)
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
        
        # Nombres de equipos: DETECTAR si el fondo es claro (Caribes) para usar texto negro
        es_visitante_claro = sum(color_visitante) / 3 > 200
        es_local_claro = sum(color_local) / 3 > 200
        
        color_texto_vis = (0, 0, 0) if es_visitante_claro else (255, 255, 255)
        color_texto_loc = (0, 0, 0) if es_local_claro else (255, 255, 255)
        
        draw.text((ancho//4, y + 113), visitante.upper(), fill=color_texto_vis, font=font_equipo, anchor="mm")
        draw.text((3*ancho//4, y + 113), local.upper(), fill=color_texto_loc, font=font_equipo, anchor="mm")
        
        # Círculo VS en el centro
        draw.ellipse([ancho//2 - 30, y + 55, ancho//2 + 30, y + 115], fill=(255, 255, 255, 255))
        draw.ellipse([ancho//2 - 30, y + 55, ancho//2 + 30, y + 115], outline=(255, 215, 0, 255), width=3)
        draw.text((ancho//2, y + 85), "VS", fill=(220, 38, 38), font=font_equipo, anchor="mm")
        
        # Franja inferior negra
        draw.rectangle([25, y + 135, ancho-25, y + altura_tarjeta - 5], fill=(20, 20, 20, 255))
        draw.rectangle([25, y + 135, ancho-25, y + altura_tarjeta - 5], outline=(255, 215, 0, 100), width=1)
        
        # Hora (arriba a la izquierda)
        draw.text((35, y + 150), f"HORA: {hora}", fill=(255, 215, 0, 255), font=font_hora, anchor="lm")
        
        # Estadio (abajo al centro)
        if lugar:
            draw.text((ancho//2, y + 175), f"ESTADIO: {lugar}", fill=(255, 255, 255, 255), font=font_estadio, anchor="mm")
        
        # 🆕 Transmisión: SOLO LOGOS (múltiples si es necesario)
        if transmision and transmision != 'Por definir':
            # Buscar todos los logos de TV que coincidan
            logos_encontrados = []
            for tv_name, tv_url in LOGOS_TV.items():
                if tv_name in transmision.lower():
                    logo_tv = descargar_logo(tv_url)
                    if logo_tv:
                        logo_tv = logo_tv.resize((30, 30), Image.Resampling.LANCZOS)
                        logos_encontrados.append(logo_tv)
            
            # Dibujar los logos encontrados (hasta 4) centrados en la franja
            if logos_encontrados:
                total_logos = len(logos_encontrados)
                espacio_logo = 40
                x_inicio = (ancho - (total_logos * espacio_logo)) // 2
                
                for j, logo_tv in enumerate(logos_encontrados):
                    x_logo = x_inicio + (j * espacio_logo) + 15
                    img.paste(logo_tv, (x_logo, y + 145), logo_tv)
    
    # 12. Footer con información
    draw.rectangle([50, alto-70, ancho-50, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-45), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 13. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
