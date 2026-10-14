import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# LISTA EXCLUSIVA DE FUENTES
FUENTES = [
    {'nombre': 'El Emergente', 'url': 'https://elemergente.com/'},
    {'nombre': 'Meridiano', 'url': 'https://meridiano.net/beisbol/beisbol-venezolano/'},
    {'nombre': 'El Carabobeño', 'url': 'https://www.el-carabobeno.com/'},
    {'nombre': 'Primicia', 'url': 'https://primicia.com.ve/deportes/'},
    {'nombre': 'La Iguana TV', 'url': 'https://www.laiguana.tv/'},
    {'nombre': 'El Diario', 'url': 'https://eldiario.com/'},
    {'nombre': 'El Estímulo', 'url': 'https://elestimulo.com/deportes/'}
]

# FILTRO RELAJADO: Más palabras clave para encontrar más noticias
PALABRAS_CLAVE_LVBP = [
    'lvbp', 'liga venezolana', 'beisbol venezolano', 'pelota criolla',
    'leones del caracas', 'leones caracas', 'navegantes del magallanes', 'navegantes magallanes',
    'tiburones de la guaira', 'tiburones guaira', 'aguilas del zulia', 'aguilas zulia',
    'tigres de aragua', 'tigres aragua', 'caribes de anzoategui', 'caribes anzoategui',
    'cardenales de lara', 'cardenales lara', 'bravos de margarita', 'bravos margarita',
    'temporada 26-27', 'temporada 2026-2027', 'lvbp 2026', 'pretemporada',
    'beisbol', 'pitcher', 'lanzador', 'bateador', 'jonron', 'home run',
    'roster', 'lista', 'contrato', 'fichaje', 'refuerzo'
]

def limpiar(txt):
    return re.sub(r'\s+', ' ', re.sub(r'https?://\S+|www\.\S+', '', txt)).strip()

def es_noticia_lvbp(titulo, desc):
    texto_completo = (titulo + ' ' + desc).lower()
    return any(palabra in texto_completo for palabra in PALABRAS_CLAVE_LVBP)

def obtener_html_con_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # CAMBIO CLAVE: domcontentloaded en vez de networkidle
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2000)
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
        articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|news|card|item', re.I))
        
        contador = 0
        for art in articulos[:20]:
            tag_titulo = art.find(['h2', 'h3', 'h1', 'a'])
            if not tag_titulo:
                continue
            
            titulo = limpiar(tag_titulo.get_text(strip=True))
            if len(titulo) < 10:
                continue
            
            enlace = fuente['url']
            tag_a = art.find('a', href=True)
            if tag_a:
                enlace = urljoin(fuente['url'], tag_a['href'])
            
            desc_tag = art.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description', re.I))
            desc = limpiar(desc_tag.get_text(strip=True)[:150]) if desc_tag else ''
            
            img_tag = art.find('img')
            img_url = urljoin(fuente['url'], img_tag.get('src')) if img_tag and img_tag.get('src') else None
            
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
