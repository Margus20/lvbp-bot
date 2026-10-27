# generadores/imagen_estadisticas.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# URLs de las mascotas de los equipos
MASCOTAS = {
    'leones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/leo.jpg',
    'navegantes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/capi.jpg',
    'tiburones': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/tibu.jpg',
    'tigres': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/tigre.jpg',
    'aguilas': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/agui.jpg',
    'cardenales': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/guarito.jpg',
    'caribes': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/caribito.jpg',
    'bravos': 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/img/mascotas/bravin.jpg',
}

# Colores por categoría (RGB) - Exactos de tu web
COLORES_CATEGORIAS = {
    'jonrones': (180, 130, 0),            # Dorado/Mostaza
    'average': (0, 50, 100),              # Azul marino
    'impulsadas': (139, 0, 0),            # Rojo vino
    'efectividad': (25, 135, 84),         # Verde
    'hits': (139, 0, 0),                  # Rojo
    'dobles': (139, 119, 0),              # Dorado
    'triples': (0, 50, 100),              # Azul
    'slugging': (139, 119, 0),            # Dorado
    'ops': (0, 50, 100),                  # Azul marino
}

NOMBRES_CATEGORIAS = {
    'jonrones': 'Jonrones (HR)',
    'average': 'Average (AVG)',
    'impulsadas': 'Carreras Impulsadas (CI)',
    'efectividad': 'Efectividad (ERA)',
    'hits': 'Hits (H)',
    'dobles': 'Dobles (2B)',
    'triples': 'Triples (3B)',
    'slugging': 'Slugging (SLG)',
    'ops': 'OPS',
}

def descargar_mascota(equipo_key):
    """Descarga la mascota del equipo"""
    url = MASCOTAS.get(equipo_key)
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

def crear_imagen_estadisticas(lideres):
    """
    Crea una imagen VERTICAL con tarjetas individuales por categoría,
    idénticas al diseño de la página web (fondo blanco, bordes redondeados, mascotas).
    """
    # Canvas vertical más alto para múltiples tarjetas
    ancho = 600
    alto = 1600
    img = Image.new('RGBA', (ancho, alto), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Fondo blanco general
    draw.rectangle([0, 0, ancho, alto], fill=(255, 255, 255, 255))
    
    # Borde dorado
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=6)
    draw.rectangle([6, 6, ancho-7, alto-7], outline=(255, 215, 0, 180), width=3)
    
    # Fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_jugador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_valor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_titulo = font_jugador = font_valor = font_numero = font_footer = ImageFont.load_default()
    
    # Título principal
    draw.text((ancho//2, 50), " LÍDERES ESTADÍSTICOS LVBP", fill=(220, 38, 38), font=font_titulo, anchor="mm")
    
    # Línea separadora
    draw.line([(50, 80), (ancho-50, 80)], fill=(255, 215, 0, 255), width=3)
    
    # Posición inicial
    y_actual = 100
    altura_categoria = 200  # Altura por tarjeta
    espacio_entre = 25
    
    # Categorías a mostrar
    categorias_principales = ['jonrones', 'average', 'impulsadas', 'efectividad', 'hits']
    
    for categoria in categorias_principales:
        if categoria not in lideres or not lideres[categoria]:
            continue
            
        color_categoria = COLORES_CATEGORIAS.get(categoria, (100, 100, 100))
        nombre_cat = NOMBRES_CATEGORIAS.get(categoria, categoria.upper())
        jugadores = lideres[categoria][:3]  # Top 3
        
        # Tarjeta con fondo blanco y bordes redondeados
        draw.rectangle([20, y_actual, ancho-20, y_actual + altura_categoria], fill=(255, 255, 255, 255))
        draw.rectangle([20, y_actual, ancho-20, y_actual + altura_categoria], outline=(200, 200, 200, 255), width=2)
        
        # Barra superior de color
        draw.rectangle([22, y_actual + 2, ancho-22, y_actual + 35], fill=color_categoria)
        draw.rectangle([22, y_actual + 2, ancho-22, y_actual + 35], outline=(255, 215, 0, 200), width=1)
        
        # Título de la categoría (texto blanco sobre barra de color)
        draw.text((ancho//2, y_actual + 19), f"🏆 {nombre_cat}", fill=(255, 255, 255, 255), font=font_jugador, anchor="mm")
        
        # Línea separadora debajo del título
        draw.line([(30, y_actual + 37), (ancho-30, y_actual + 37)], fill=(240, 240, 240, 255), width=1)
        
        # Dibujar cada jugador en fila horizontal
        y_jugador = y_actual + 50
        altura_fila = 45
        
        for i, jugador in enumerate(jugadores):
            y = y_jugador + (i * (altura_fila + 5))
            
            # Fondo de la fila (gris muy claro alternado)
            if i % 2 == 0:
                draw.rectangle([30, y, ancho-30, y + altura_fila], fill=(250, 250, 250, 255))
            
            # 1. Número de posición (#1, #2, #3)
            draw.text((45, y + 23), f"#{i+1}", fill=color_categoria, font=font_numero, anchor="mm")
            
            # 2. Mascota del equipo (círculo de 35x35)
            equipo_key = jugador.get('equipo', '')
            mascota = descargar_mascota(equipo_key)
            if mascota:
                mascota = mascota.resize((35, 35), Image.Resampling.LANCZOS)
                # Crear máscara circular
                mask = Image.new('L', (35, 35), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 35, 35), fill=255)
                img.paste(mascota, (70, y + 5), mask)
            
            # 3. Nombre del jugador
            nombre = jugador.get('nombre', 'Desconocido')
            # Limpiar el nombre (quitar posición si está pegada)
            nombre_limpio = nombre.split('(')[0].strip() if '(' in nombre else nombre
            nombre_mostrar = nombre_limpio[:20]
            draw.text((115, y + 23), nombre_mostrar, fill=(0, 0, 0, 255), font=font_jugador, anchor="lm")
            
            # 4. Valor estadístico (rectángulo redondeado a la derecha)
            valor = str(jugador.get('valor', '0'))
            # Fondo del valor
            draw.rounded_rectangle([ancho-100, y + 8, ancho-30, y + altura_fila - 8], radius=8, fill=color_categoria)
            draw.text((ancho-65, y + 23), valor, fill=(255, 255, 255, 255), font=font_valor, anchor="mm")
        
        y_actual += altura_categoria + espacio_entre
    
    # Footer
    draw.rectangle([80, alto-50, ancho-80, alto-20], fill=(20, 24, 82, 255))
    draw.text((ancho//2, alto-35), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
