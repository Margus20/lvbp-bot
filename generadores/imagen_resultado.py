# generadores/imagen_resultado.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from datetime import datetime, timedelta
import random  # 🆕 Agregado para la textura de fondo

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

# Colores de fondo por equipo (basados en tu página)
COLORES_FONDO = {
    'cardenales': (220, 38, 38),        # Rojo
    'caribes': (245, 245, 245),         # Gris claro/blanco
    'tigres': (0, 38, 92),              # Azul oscuro
    'bravos': (78, 173, 173),           # Turquesa
    'leones': (0, 32, 96),              # Azul marino
    'aguilas': (249, 97, 0),            # Naranja
    'tiburones': (41, 41, 249),         # Azul eléctrico
    'magallanes': (91, 183, 230),       # Azul claro
}

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
    return 'lvbp'

def descargar_logo(equipo_key):
    """Descarga el logo desde URL"""
    url = LOGOS.get(equipo_key, LOGOS['lvbp'])
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

# 🆕 Función para dibujar la textura de pelotas
def dibujar_pelota_béisbol(draw, x, y, radio):
    """Dibuja una pelota de béisbol sutil en el fondo"""
    draw.ellipse([x-radio, y-radio, x+radio, y+radio], fill=(245, 245, 245, 255))
    draw.arc([x-radio+3, y-radio+3, x+radio-3, y+radio-3], start=45, end=135, fill=(220, 38, 38, 80), width=2)
    draw.arc([x-radio+3, y-radio+3, x+radio-3, y+radio-3], start=225, end=315, fill=(220, 38, 38, 80), width=2)

def crear_imagen_resultados(juegos, fecha_hoy=None):
    """
    Crea una imagen VERTICAL con TODOS los resultados del día,
    centrados verticalmente y con textura de fondo.
    """
    
    # 1. Canvas vertical un poco más alto (1200) para que 4 juegos quepan con holgura al centrarse
    ancho = 650
    alto = 1200
    img = Image.new('RGBA', (ancho, alto), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. 🆕 Textura de fondo (pelotas de béisbol sutiles en el blanco)
    random.seed(42)  # Para que el patrón sea siempre el mismo y elegante
    for _ in range(15):
        px = random.randint(40, ancho-40)
        py = random.randint(140, alto-80)
        pr = random.randint(15, 30)
        dibujar_pelota_béisbol(draw, px, py, pr)
    
    # 3. Borde dorado brillante
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # 4. Cargar fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_equipo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_marcador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_innings = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_pitcher = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_fecha = font_equipo = font_marcador = font_innings = font_pitcher = font_footer = ImageFont.load_default()
    
    # 5. Logo del canal en la esquina superior izquierda
    logo_canal = descargar_logo('lvbp')
    if logo_canal:
        logo_canal = logo_canal.resize((50, 50), Image.Resampling.LANCZOS)
        img.paste(logo_canal, (15, 15), logo_canal)
    
    # 6. Título (SIN emoji y SIN sombra duplicada)
    draw.text((ancho//2, 70), "RESULTADOS", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # 7. Fecha: por defecto usa la fecha de ayer (cuando fueron los juegos)
    if not fecha_hoy:
        fecha_ayer = datetime.now() - timedelta(days=1)
        fecha_hoy = fecha_ayer.strftime('%d de %B de %Y').capitalize()
    draw.text((ancho//2, 105), fecha_hoy, fill=(220, 38, 38), font=font_fecha, anchor="mm")
    
    # Línea separadora dorada
    draw.line([(50, 130), (ancho-50, 130)], fill=(255, 215, 0, 255), width=3)
    
    # 8. 🆕 CÁLCULO DE CENTRADO VERTICAL
    num_juegos = len(juegos[:4])
    altura_tarjeta = 220
    espacio_entre = 20
    altura_total_tarjetas = (num_juegos * altura_tarjeta) + ((num_juegos - 1) * espacio_entre)
    
    # Espacio disponible (restando ~150px del header y ~70px del footer)
    espacio_disponible = alto - 150 - 70
    y_inicio = 150 + ((espacio_disponible - altura_total_tarjetas) // 2)
    
    # 9. Dibujar cada juego como tarjeta profesional
    for i, juego in enumerate(juegos[:4]):  # Máximo 4 juegos
        visitante = juego.get('visitante', '???')
        local = juego.get('local', '???')
        score_vis = str(juego.get('scoreVisitante', '0'))
        score_loc = str(juego.get('scoreLocal', '0'))
        innings = str(juego.get('innings', '9'))
        fecha_juego = juego.get('fecha', '')
        
        # Pitchers
        pitcher_g = juego.get('pitcherGanador', '')
        pitcher_p = juego.get('pitcherPerdedor', '')
        pitcher_s = juego.get('pitcherSalvador', '')
        
        y = y_inicio + (i * (altura_tarjeta + espacio_entre))
        
        # Obtener colores de los equipos
        color_vis = COLORES_FONDO.get(detectar_equipo(visitante), (100, 100, 100))
        color_loc = COLORES_FONDO.get(detectar_equipo(local), (100, 100, 100))
        
        # Tarjeta con bordes redondeados (El fondo blanco sólido tapa la textura de atrás, ¡perfecto!)
        draw.rectangle([20, y, ancho-20, y + altura_tarjeta], fill=(255, 255, 255, 255))
        draw.rectangle([20, y, ancho-20, y + altura_tarjeta], outline=(255, 215, 0, 200), width=2)
        
        # === PARTE SUPERIOR: EQUIPOS ===
        # Mitad izquierda (Visitante)
        draw.rectangle([25, y + 5, ancho//2 - 5, y + 115], fill=color_vis)
        
        # Mitad derecha (Local)
        draw.rectangle([ancho//2 + 5, y + 5, ancho-25, y + 115], fill=color_loc)
        
        # Línea divisoria dorada
        draw.line([(ancho//2, y + 5), (ancho//2, y + 115)], fill=(255, 215, 0, 255), width=3)
        
        # Logo visitante (grande 90x90)
        logo_vis = descargar_logo(detectar_equipo(visitante))
        if logo_vis:
            logo_vis = logo_vis.resize((90, 90), Image.Resampling.LANCZOS)
            img.paste(logo_vis, (ancho//4 - 45, y + 10), logo_vis)
        
        # Logo local (grande 90x90)
        logo_loc = descargar_logo(detectar_equipo(local))
        if logo_loc:
            logo_loc = logo_loc.resize((90, 90), Image.Resampling.LANCZOS)
            img.paste(logo_loc, (3*ancho//4 - 45, y + 10), logo_loc)
        
        # Nombres de equipos: DETECTAR si el fondo es claro (Caribes) para usar texto negro
        es_visitante_claro = sum(color_vis) / 3 > 200
        es_local_claro = sum(color_loc) / 3 > 200
        
        color_texto_vis = (0, 0, 0) if es_visitante_claro else (255, 255, 255)
        color_texto_loc = (0, 0, 0) if es_local_claro else (255, 255, 255)
        
        draw.text((ancho//4, y + 103), visitante.upper(), fill=color_texto_vis, font=font_equipo, anchor="mm")
        draw.text((3*ancho//4, y + 103), local.upper(), fill=color_texto_loc, font=font_equipo, anchor="mm")
        
        # Círculo VS
        draw.ellipse([ancho//2 - 35, y + 40, ancho//2 + 35, y + 80], fill=(255, 255, 255, 255))
        draw.ellipse([ancho//2 - 35, y + 40, ancho//2 + 35, y + 80], outline=(255, 215, 0, 255), width=3)
        draw.text((ancho//2, y + 60), "VS", fill=(220, 38, 38), font=font_equipo, anchor="mm")
        
        # === FRANJA INFERIOR NEGRA ===
        draw.rectangle([25, y + 120, ancho-25, y + altura_tarjeta - 5], fill=(20, 20, 20, 255))
        draw.rectangle([25, y + 120, ancho-25, y + altura_tarjeta - 5], outline=(255, 215, 0, 100), width=1)
        
        # Marcador grande (centro)
        draw.text((ancho//2 - 30, y + 150), score_vis, fill=(255, 215, 0, 255), font=font_marcador, anchor="rm")
        draw.text((ancho//2, y + 150), "-", fill=(255, 255, 255, 255), font=font_marcador, anchor="mm")
        draw.text((ancho//2 + 30, y + 150), score_loc, fill=(255, 215, 0, 255), font=font_marcador, anchor="lm")
        
        # Innings en una sola línea (esquina superior derecha de la franja)
        innings_texto = f"{innings} INNINGS"
        draw.text((ancho - 35, y + 128), innings_texto, fill=(255, 215, 0, 255), font=font_innings, anchor="rm")
        
        # Fecha del juego (centro, debajo del marcador)
        draw.text((ancho//2, y + 175), fecha_juego, fill=(200, 200, 200, 255), font=font_pitcher, anchor="mm")
        
        # Pitchers (alineados a la izquierda con espaciado fijo)
        x_pitchers = 35
        y_pitchers = y + 195
        
        if pitcher_g:
            draw.text((x_pitchers, y_pitchers), f"G: {pitcher_g}", fill=(76, 175, 80), font=font_pitcher, anchor="lm")
            x_pitchers += 170  # 🆕 Aumentado ligeramente para mayor seguridad
            
        if pitcher_p:
            draw.text((x_pitchers, y_pitchers), f"P: {pitcher_p}", fill=(244, 67, 54), font=font_pitcher, anchor="lm")
            x_pitchers += 170
            
        if pitcher_s:
            draw.text((x_pitchers, y_pitchers), f"S: {pitcher_s}", fill=(33, 150, 243), font=font_pitcher, anchor="lm")
    
    # 10. Footer
    draw.rectangle([80, alto-60, ancho-80, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # 11. Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
