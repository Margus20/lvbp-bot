# generadores/imagen_estadisticas.py
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# Colores por categoría (fondos)
COLORES_CATEGORIAS = {
    'carreras': (180, 50, 50),      # Rojo oscuro
    'average': (20, 24, 82),        # Azul oscuro
    'hr': (180, 130, 0),            # Dorado/Mostaza
    'era': (25, 135, 84),           # Verde
    'ci': (139, 0, 0),              # Rojo vino
    'slg': (139, 119, 0),           # Dorado oscuro
    'ops': (0, 50, 100),            # Azul marino
    'hits': (139, 0, 0),            # Rojo
    'dobles': (139, 119, 0),        # Dorado
    'triples': (0, 50, 100),        # Azul
}

NOMBRES_CATEGORIAS = {
    'carreras': 'Carreras (C)',
    'average': 'Average (AVG)',
    'hr': 'Jonrones (HR)',
    'era': 'Efectividad (ERA)',
    'ci': 'Carreras Impulsadas (CI)',
    'slg': 'Slugging (SLG)',
    'ops': 'OPS',
    'hits': 'Hits (H)',
    'dobles': 'Dobles (2B)',
    'triples': 'Triples (3B)',
}

def descargar_foto_jugador(url):
    """Descarga la foto del jugador"""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except:
        pass
    return None

def crear_imagen_estadisticas(lideres):
    """
    Crea una imagen VERTICAL con las principales categorías estadísticas
    mostrando el TOP 3 de cada una.
    """
    # Canvas vertical grande (600x1200)
    ancho = 600
    alto = 1200
    img = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo con gradiente azul oscuro
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
        font_jugador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_valor = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_numero = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_titulo = font_categoria = font_jugador = font_valor = font_numero = font_footer = ImageFont.load_default()
    
    # Título
    draw.text((ancho//2 + 1, 51), "📊 LÍDERES ESTADÍSTICOS LVBP", fill=(0, 0, 0, 150), font=font_titulo, anchor="mm")
    draw.text((ancho//2, 50), " LÍDERES ESTADÍSTICOS LVBP", fill=(255, 215, 0, 255), font=font_titulo, anchor="mm")
    
    # Línea separadora
    draw.line([(50, 90), (ancho-50, 90)], fill=(255, 215, 0, 255), width=2)
    
    # Posición inicial
    y_actual = 110
    altura_categoria = 180
    espacio_entre = 20
    
    # Categorías a mostrar (máximo 5 para que quepan bien)
    categorias_principales = ['hr', 'average', 'ci', 'era', 'hits']
    
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
        
        # Jugadores (Top 3 en horizontal)
        x_inicial = 60
        espacio_jugador = (ancho - 120) // 3
        
        for i, jugador in enumerate(jugadores):
            x = x_inicial + (i * espacio_jugador) + (espacio_jugador // 2)
            y_jugador = y_actual + 70
            
            # Número de posición (círculo dorado)
            draw.ellipse([x - 25, y_jugador - 25, x + 25, y_jugador + 25], fill=(255, 215, 0, 255))
            draw.text((x, y_jugador), f"#{i+1}", fill=(0, 0, 0, 255), font=font_numero, anchor="mm")
            
            # Foto del jugador (si hay URL)
            foto_url = jugador.get('foto', '')
            if foto_url:
                foto = descargar_foto_jugador(foto_url)
                if foto:
                    foto = foto.resize((50, 50), Image.Resampling.LANCZOS)
                    img.paste(foto, (x - 25, y_jugador + 15), foto)
            
            # Nombre del jugador (abreviado)
            nombre = jugador.get('nombre', 'Desconocido')
            # Extraer solo el apellido o nombre corto
            nombre_corto = nombre.split()[0][:12].upper() if nombre else 'N/A'
            draw.text((x, y_jugador + 80), nombre_corto, fill=(255, 255, 255, 255), font=font_jugador, anchor="mm")
            
            # Valor estadístico
            valor = str(jugador.get('valor', '0'))
            draw.text((x, y_jugador + 110), valor, fill=(255, 215, 0, 255), font=font_valor, anchor="mm")
        
        y_actual += altura_categoria + espacio_entre
    
    # Footer
    draw.rounded_rectangle([100, alto-60, ancho-100, alto-20], radius=15, fill=(0, 0, 0, 200))
    draw.text((ancho//2, alto-40), "LVBP al Día - margus20.github.io", fill=(255, 255, 255, 255), font=font_footer, anchor="mm")
    
    # Guardar en memoria
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr
