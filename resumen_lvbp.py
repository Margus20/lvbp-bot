import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 1. URLS DIRECCIONADAS A SECCIONES DE BÉISBOL Y DEPORTES
FUENTES = [
    {'nombre': 'El Emergente', 'url': 'https://elemergente.com/'},
    {'nombre': 'Meridiano', 'url': 'https://meridiano.net/beisbol/beisbol-venezolano/'},
    {'nombre': 'El Carabobeño', 'url': 'https://www.el-carabobeno.com/seccion/deportes/'},
    {'nombre': 'Primicia', 'url': 'https://primicia.com.ve/deportes/'},
    {'nombre': 'La Iguana TV', 'url': 'https://www.laiguana.tv/deportes/'},
    {'nombre': 'El Diario', 'url': 'https://eldiario.com/categoria/deportes/'},
    {'nombre': 'El Estímulo', 'url': 'https://elestimulo.com/deportes/'}
]

# 2. EQUIPOS Y TÉRMINOS OBLIGATORIOS DE LVBP (Evita confusión con MLB)
EQUIPOS_LVBP = [
    'lvbp', 'liga venezolana', 'beisbol venezolano', 'pelota criolla',
    'leones del caracas', 'leones', 'caracas bbc',
    'navegantes del magallanes', 'navegantes', 'magallanes',
    'tiburones de la guaira', 'tiburones', 'guaira',
    'aguilas del zulia', 'aguilas', 'zulia',
    'tigres de aragua', 'tigres', 'aragua',
    'caribes de anzoategui', 'caribes', 'anzoategui',
    'cardenales de lara', 'cardenales', 'lara',
    'bravos de margarita', 'bravos', 'margarita'
]

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

def es_noticia_lvbp(titulo, desc):
    if es_spam(titulo):
        return False
    texto_completo = (titulo + ' ' + desc).lower()
    # Si la fuente es El Emergente (que es 100% béisbol), aceptamos más fácil
    return any(equipo in texto_completo for equipo in EQUIPOS_LVBP)

def obtener_html_con_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Bloquear imágenes/css para acelerar la carga en GitHub Actions
            page.route("**/*.{png,jpg,jpeg,svg,css,woff,woff2}", lambda route: route.abort())
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
        
        # Estrategia de Búsqueda Mejorada: Buscar enlaces directos que contengan títulos
        articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|news|card|item|article|story', re.I))
        
        if not articulos:
            # Respaldo: buscar todos los encabezados con enlace
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
            
            # Buscar Enlace
            enlace = fuente['url']
            tag_a = art if art.name == 'a' else art.find('a', href=True)
            if tag_a and tag_a.get('href'):
                href = tag_a['href']
                enlace = href if href.startswith('http') else urljoin(fuente['url'], href)

            # Buscar Descripción
            desc = ''
            p_tag = art.find('p')
            if p_tag:
                desc = limpiar(p_tag.get_text(strip=True)[:200])

            # Buscar Imagen
            img_url = None
            img_tag = art.find('img')
            if img_tag:
                src = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('srcset')
                if src:
                    # En caso de srcset, tomar la primera URL
                    src = src.split(',')[0].split(' ')[0]
                    img_url = urljoin(fuente['url'], src)

            # Validación Especial para El Emergente (Sitio 100% de Béisbol)
            if fuente['nombre'] == 'El Emergente' and not es_spam(titulo):
                paso_filtro = True
            else:
                paso_filtro = es_noticia_lvbp(titulo, desc)

            if paso_filtro:
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
    
