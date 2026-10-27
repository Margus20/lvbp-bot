# generadores/imagen_estadisticas.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# 🆕 Agregamos las mascotas para que se vea igual a la web
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

def descargar_mascota(equipo_key):
    """Descarga la mascota del equipo en formato circular"""
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

# Colores por categoría (fondos)
COLORES_CATEGORIAS = {
    'jonrones': (180, 130, 0),            # Dorado/Mostaza
    'average': (20, 24, 82),              # Azul oscuro
    'impulsadas': (139, 0, 0),            # Rojo vino
    'efectividad': (25, 135, 84),         # Verde
    'hits': (139, 0, 0),                  # Rojo
}

NOMBRES_CATEGORIAS = {
    'jonrones': 'Jonrones (HR)',
    'average': 'Average (AVG)',
    'impulsadas': 'Carreras Impulsadas (CI)',
    'efectividad': 'Efectividad (ERA)',
    'hits': 'Hits (H)',
}

def crear_imagen_estadisticas(lideres):
    """
    Crea una imagen VERTICAL con las principales categorías estadísticas
    mostrando el TOP 3 de cada una en FILAS HORIZONTALES (idéntico a la web).
    """
    # 🆕 Canvas un poco más alto (1300) para que quepan bien las 3 filas por categoría
    ancho = 600
    alto = 1300
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo con gradiente azul oscuro (tu código original)
    for y in range(alto):
        r = int(20 + (0 - 20) * (y / alto))
        g = int(24 + (0 - 24) * (y / alto))
        b = int(82 + (40 - 82) * (y / alto))
        draw.line((0, y, ancho, y), fill=(r, g, b, 255))
    
    # Borde dorado
    draw.rectangle([0, 0, ancho-1, alto-1], outline=(255, 215, 0, 255), width=5)
    draw.rectangle([8, 8, ancho-9, alto-9], outline=(255, 215, 0, 150), width=2)
    
    # Fuentes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_categoria = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_jugador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_valor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_categoria = font_jugador = font_valor = font_numero = font_footer = ImageFont.load_default()
    
    # Título
    draw.text((ancho//2, 50), "📊 LÍDERES ESTADÍSTICOS LVBP", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # Línea separadora
    draw.line([(50, 90), (ancho-50, 90)], fill=(255, 215, 0, 255), width=2)
    
    # Posición inicial
    y_actual = 110
    altura_categoria = 220  # 🆕 Aumentado para acomodar 3 filas horizontales
    espacio_entre = 20
    
    # Categorías a mostrar
    categorias_principales = ['jonrones', 'average', 'impulsadas', 'efectividad', 'hits']
    
    for categoria in categorias_principales:
        if categoria not in lideres or not lideres[categoria]:
            continue
            
        color_fondo = COLORES_CATEGORIAS.get(categoria, (100, 100, 100))
        nombre_cat = NOMBRES_CATEGORIAS.get(categoria, categoria.upper())
        jugadores = lideres[categoria][:3]  # Top 3
        
        # Fondo de la categoría
        draw.rounded_rectangle([20, y_actual, ancho-20, y_actual + altura_categoria], radius=15, fill=(color_fondo[0], color_fondo[1], color_fondo[2], 200))
        draw.rounded_rectangle([20, y_actual, ancho-20, y_actual + altura_categoria], radius=15, outline=(255, 215, 0, 150), width=2)
        
        # Título de la categoría
        draw.text((ancho//2, y_actual + 25), f"🏆 {nombre_cat}", fill=(255, 255, 255, 255), font=font_categoria, anchor="mm")
        
        # 🆕 Jugadores en FILAS HORIZONTALES (igual que tu página web)
        y_fila = y_actual + 60
        altura_fila = 50
        
        for i, jugador in enumerate(jugadores):
            y = y_fila + (i * (altura_fila + 10))
            
            # 1. Número de posición
            draw.text((45, y + 25), f"#{i+1}", fill=(255, 215, 0, 255), font=font_numero, anchor="mm")
            
            # 2. Mascota del equipo (círculo de 40x40)
            equipo_key = jugador.get('equipo', '')
            mascota = descargar_mascota(equipo_key)
            if mascota:
                mascota = mascota.resize((40, 40), Image.Resampling.LANCZOS)
                # Crear máscara circular
                mask = Image.new('L', (40, 40), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 40, 40), fill=255)
                img.paste(mascota, (70, y + 5), mask)
            
            # 3. Nombre del jugador (formato "M. Vargas" o el que venga en el JS)
            nombre = jugador.get('nombre', 'Desconocido')
            nombre_mostrar = nombre[:22] + "..." if len(nombre) > 22 else nombre
            draw.text((120, y + 25), nombre_mostrar, fill=(255, 255, 255, 255), font=font_jugador, anchor="lm")
            
            # 4. Valor estadístico (círculo blanco a la derecha)
            valor = str(jugador.get('valor', '0'))
            draw.ellipse([ancho-90, y + 5, ancho-50, y + 45], fill=(255, 255, 255, 255))
            draw.text((ancho-70, y + 25), valor, fill=color_fondo, font=font_valor, anchor="mm")
            
        y_actual += altura_categoria + espacio_entre
    
    # Footer
    draw.rounded_rectangle([100, alto-60, ancho-100, alto-20], radius=15, fill=(0, 0, 0, 200))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
