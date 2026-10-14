import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 1. URLS DIRECCIONADAS A SECCIONES DE BÉISBOL/DEPORTES
FUENTES = [
    {'nombre': 'El Emergente', 'url': 'https://elemergente.com/'},
    {'nombre': 'Meridiano', 'url': 'https://meridiano.net/beisbol/beisbol-venezolano/'},
    {'nombre': 'El Carabobeño', 'url': 'https://www.el-carabobeno.com/seccion/deportes/'},
    {'nombre': 'Primicia', 'url': 'https://primicia.com.ve/deportes/'},
    {'nombre': 'La Iguana TV', 'url': 'https://www.laiguana.tv/deportes/'},
    {'nombre': 'El Diario', 'url': 'https://eldiario.com/categoria/deportes/'},
    {'nombre': 'El Estímulo', 'url': 'https://elestimulo.com/deportes/'}
]

# 2. FILTRO DE EXCLUSIÓN: OTRAS LIGAS Y OTROS DEPORTES
OTRAS_LIGAS_Y_DEPORTES = [
    'atlanta', 'detroit', 'grandes ligas', 'mlb', 'yankees', 'red sox', 
    'dodgers', 'astros', 'padres de san diego', 'mets', 'reds', 'cubs',
    'escogido', 'cibaeñas', 'cibao', 'licey', 'lidom', 'toros del este', 
    'estrellas orientales', 'tomateros', 'naranjeros', 'yaquis', 'lmp', 
    'liga del pacifico', 'vinotinto', 'fútbol', 'futbol', 'champions league', 
    'liga futve', 'real madrid', 'barcelona', 'messi', 'ronaldo', 'nba', 
    'baloncesto', 'basket', 'formula 1', 'f1', 'red bull', 'ferrari', 
    'tenis', 'atp', 'wta', 'boxeo', 'ufc', 'pádel', 'padel'
]

# 3. PALABRAS ANTI-SPAM
PALABRAS_SPAM = [
    'suscríbete', 'suscribete', 'suscribirse', 'boletín', 'boletin', 'newsletter',
    'contacto', 'políticas', 'politicas', 'privacidad', 'términos', 'terminos',
    'cookies', 'publicidad', 'anúnciate', 'anunciate', 'aviso legal',
    'mapa del sitio', 'acerca de', 'about us', 'trabaja con nosotros'
]

def limpiar(txt):
    return re.sub(r'\s+', ' ', re.sub(r'https?://\S+|www\.\S+', '', txt)).strip()

def es_spam(titulo):
    t = titulo.lower()
    return any(palabra in t for palabra in PALABRAS_SPAM)

def es_noticia_lvbp_precisa(titulo, desc, fuente_nombre):
    """Filtra y asegura que la noticia pertenezca EXCLUSIVAMENTE a la LVBP."""
    texto = (titulo + ' ' + desc).lower()
    
    # 1. Descartar si es spam/publicidad
    if es_spam(titulo):
        return False

    # 2. Descartar si menciona otras ligas de béisbol u otros deportes
    if any(descarte in texto for descarte in OTRAS_LIGAS_Y_DEPORTES):
        return False

    # 3. Caso especial El Emergente (Sitio especializado, pero aún así verificamos términos base)
    if fuente_nombre == 'El Emergente':
        # Solo damos el pase si al menos tiene un término de béisbol genérico o de LVBP
        if any(t in texto for t in ['beisbol', 'pelota', 'lvbp', 'liga venezolana']):
            return True

    # 4. Filtro para nombres de equipos ambiguos
    if 'bravos' in texto and not any(k in texto for k in ['margarita', 'lvbp', 'liga venezolana', 'pelota criolla']):
        return False
    if 'leones' in texto and not any(k in texto for k in ['caracas', 'lvbp', 'liga venezolana', 'pelota criolla']):
        return False
    if 'tigres' in texto and not any(k in texto for k in ['aragua', 'lvbp', 'liga venezolana', 'pelota criolla']):
        return False
    if 'aguilas' in texto and not any(k in texto for k in ['zulia', 'lvbp', 'liga venezolana', 'pelota criolla']):
        return False

    # 5. Términos inequívocos de la LVBP (Actualizado)
    TERMINOS_UNICOS_LVBP = [
        'lvbp', 'magallanes', 'navegantes', 'tiburones', 'la guaira', 
        'cardenales de lara', 'cardenales', 'caribes de anzoategui', 'caribes', 
        'pelota criolla', 'liga venezolana', 'round robin', 'serie final', 'semifinal'
    ]
    
    return any(termino in texto for termino in TERMINOS_UNICOS_LVBP)

def obtener_html_con_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Bloquear carga de recursos pesados para acelerar la ejecución
            page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2}", lambda route: route.abort())
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"  ⚠️ Error con Playwright en {url}: {e}")
        return None

def obtener_noticias_externas():
    noticias = []
    print("📰 Buscando en fuentes externas de LVBP con Playwright...")
    
    for fuente in FUENTES:
        print(f"  - {fuente['nombre']}...")
        html = obtener_html_con_playwright(fuente['url'])
        
        if not html:
            print(f"    ⚠️ No se pudo obtener HTML de {fuente['nombre']}")
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar contenedores principales de noticias
        articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|news|card|item|article|story', re.I))
        
        if not articulos:
            articulos = soup.find_all(['h2', 'h3', 'h4'])

        contador = 0
        for art in articulos[:30]:
            # Extraer título
            if art.name in ['h2', 'h3', 'h4']:
                tag_titulo = art
            else:
                tag_titulo = art.find(['h1', 'h2', 'h3', 'h4', 'a'])
                
            if not tag_titulo:
                continue
            
            titulo = limpiar(tag_titulo.get_text(strip=True))
            
            if len(titulo) < 18 or len(titulo) > 200:
                continue
            
            # Buscar Enlace (MEJORA: Filtrar enlaces basura)
            enlace = fuente['url']
            tag_a = art if art.name == 'a' else art.find('a', href=True)
            if tag_a and tag_a.get('href'):
                href = tag_a['href'].strip()
                # Ignorar enlaces internos, scripts o correos
                if href and not href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                    enlace = href if href.startswith('http') else urljoin(fuente['url'], href)

            # Buscar Descripción (MEJORA: Exigir longitud mínima para evitar "Por: Redacción")
            desc = ''
            p_tag = art.find('p')
            if p_tag:
                desc_candidata = limpiar(p_tag.get_text(strip=True))
                if len(desc_candidata) > 30:
                    desc = desc_candidata[:200]

            # Buscar Imagen (MEJORA: Validar que no sea un placeholder o base64 diminuto)
            img_url = None
            img_tag = art.find('img')
            if img_tag:
                src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset')
                if src:
                    src = src.split(',')[0].split(' ')[0].strip()
                    # Validar que sea una URL real y no un placeholder diminuto
                    if src.startswith('http') and len(src) > 25 and 'placeholder' not in src.lower():
                        img_url = urljoin(fuente['url'], src)

            # FILTRADO DE NOTICIA: Validar exclusividad de LVBP
            if es_noticia_lvbp_precisa(titulo, desc, fuente['nombre']):
                noticias.append({
                    'titulo': titulo,
                    'desc': desc if desc else 'Noticia de la LVBP',
                    'img': img_url,
                    'enlace': enlace,
                    'fuente': fuente['nombre'],
                    'tipo': 'externa'
                })
                contador += 1
        
        print(f"    ✅ {contador} noticias de LVBP encontradas")
            
    print(f"  ✅ Total: {len(noticias)} noticias válidas de LVBP.")
    return noticias
