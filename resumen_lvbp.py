import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# LISTA EXCLUSIVA DE FUENTES (Solo las que tú aprobaste)
FUENTES = [
    {'nombre': 'El Emergente', 'url': 'https://elemergente.com/'},
    {'nombre': 'Meridiano', 'url': 'https://meridiano.net/beisbol/beisbol-venezolano/'},
    {'nombre': 'El Carabobeño', 'url': 'https://www.el-carabobeno.com/'},
    {'nombre': 'Primicia', 'url': 'https://primicia.com.ve/deportes/'},
    {'nombre': 'La Iguana TV', 'url': 'https://www.laiguana.tv/'},
    {'nombre': 'El Diario', 'url': 'https://eldiario.com/'},
    {'nombre': 'El Estímulo', 'url': 'https://elestimulo.com/deportes/'}
]

# FILTRO ESTRICTO: La noticia DEBE contener al menos una de estas palabras
# Usamos los nombres COMPLETOS de los equipos para evitar confusiones con otros países
PALABRAS_CLAVE_LVBP = [
    'lvbp', 'liga venezolana de béisbol', 'beisbol venezolano', 'pelota criolla',
    'leones del caracas', 'navegantes del magallanes', 'tiburones de la guaira',
    'aguilas del zulia', 'tigres de aragua', 'caribes de anzoategui',
    'cardenales de lara', 'bravos de margarita',
    'temporada 26-27', 'temporada 2026-2027', 'lvbp 2026'
]

def limpiar(txt):
    return re.sub(r'\s+', ' ', re.sub(r'https?://\S+|www\.\S+', '', txt)).strip()

def es_noticia_lvbp(titulo, desc):
    """Verifica estrictamente que la noticia sea de béisbol venezolano."""
    texto_completo = (titulo + ' ' + desc).lower()
    return any(palabra in texto_completo for palabra in PALABRAS_CLAVE_LVBP)

def obtener_html_con_playwright(url):
    """
    Usa Playwright para obtener el HTML renderizado de una página.
    Esto bypassa el anti-bot porque actúa como un navegador real.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navegar y esperar a que cargue todo
            page.goto(url, wait_until="networkidle", timeout=20000)
            
            # Esperar un poco más para que cargue contenido dinámico
            page.wait_for_timeout(2000)
            
            # Obtener el HTML completo ya renderizado
            html = page.content()
            browser.close()
            
            return html
    except Exception as e:
        print(f"  ⚠️ Error con Playwright en {url}: {e}")
        return None

def obtener_noticias_externas():
    """Scrapea las fuentes aprobadas usando Playwright y devuelve solo noticias filtradas de LVBP."""
    noticias = []
    print("📰 Buscando en fuentes externas de LVBP con Playwright...")
    
    for fuente in FUENTES:
        print(f"  - {fuente['nombre']}...")
        
        # Obtener HTML renderizado con Playwright
        html = obtener_html_con_playwright(fuente['url'])
        
        if not html:
            print(f"    ⚠️ No se pudo obtener HTML de {fuente['nombre']}")
            continue
        
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar artículos, entradas o tarjetas de noticias
        articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|news|card|item', re.I))
        
        contador = 0
        for art in articulos[:15]:
            tag_titulo = art.find(['h2', 'h3', 'h1', 'a'])
            if not tag_titulo:
                continue
            
            titulo = limpiar(tag_titulo.get_text(strip=True))
            if len(titulo) < 15:
                continue
            
            # Buscar enlace
            enlace = fuente['url']
            tag_a = art.find('a', href=True)
            if tag_a:
                enlace = urljoin(fuente['url'], tag_a['href'])
            
            # Buscar descripción
            desc_tag = art.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description', re.I))
            desc = limpiar(desc_tag.get_text(strip=True)[:150]) if desc_tag else ''
            
            # Buscar imagen
            img_tag = art.find('img')
            img_url = urljoin(fuente['url'], img_tag.get('src')) if img_tag and img_tag.get('src') else None
            
            # FILTRO ESTRICTO: Si no es LVBP, se descarta
            if not es_noticia_lvbp(titulo, desc):
                continue
            
            noticias.append({
                'titulo': titulo,
                'desc': desc,
                'img': img_url,
                'enlace': enlace,
                'fuente': fuente['nombre'],
                'tipo': 'externa'
            })
            contador += 1
        
        print(f"    ✅ {contador} noticias de LVBP encontradas")
            
    print(f"  ✅ Total: {len(noticias)} noticias válidas de LVBP.")
    return noticias
