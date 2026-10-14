import requests
import json
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

LVBP_RESULTADOS = "https://stats.lvbp.com/resultados.php"
LVBP_POSICIONES = "https://stats.lvbp.com/posiciones.php"

EQUIPOS_LVBP = [
    'leones del caracas', 'navegantes del magallanes', 'tiburones de la guaira',
    'aguilas del zulia', 'tigres de aragua', 'caribes de anzoategui', 'caribes de anzoátegui',
    'cardenales de lara', 'bravos de margarita'
]

def capturar_api_con_playwright(url):
    """Captura respuestas JSON/HTML ocultas usando Network Interception optimizado."""
    print(f"  🕵️ Interceptando red en {url}...")
    datos_capturados = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # OPTIMIZACIÓN: Bloquear recursos pesados para acelerar la carga x3
            page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,mp4}", lambda route: route.abort())
            
            def handle_response(response):
                url_resp = response.url.lower()
                if ('lvbp' in url_resp or 'stats' in url_resp) and response.status == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    # Capturamos JSON, JS y también text/plain que a veces contiene JSON
                    if any(ct in content_type for ct in ['json', 'javascript', 'text/plain']):
                        try:
                            body = response.json()
                            datos_capturados.append({'url': response.url, 'data': body, 'type': 'json'})
                            print(f"  ✅ JSON capturado: {response.url}")
                        except:
                            # Fallback a texto si el parseo JSON falla
                            try:
                                body = response.text()
                                if len(body) > 500 and ('team' in body.lower() or 'game' in body.lower()):
                                    datos_capturados.append({'url': response.url, 'data': body, 'type': 'html'})
                            except:
                                pass
            
            page.on("response", handle_response)
            
            # MEJORA 1: Espera inteligente en lugar de tiempo ciego
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                # Espera a que aparezca una tabla o un contenedor de juegos (máx 5 seg)
                page.wait_for_selector('table, .game, .match, .card, .boxscore', timeout=5000)
            except PlaywrightTimeout:
                pass # No pasa nada, continuamos con el HTML que haya cargado
            
            page.wait_for_timeout(1500) # Pequeña pausa final para scripts rezagados
            browser.close()
            
        return datos_capturados
    except Exception as e:
        print(f"  ⚠️ Error con Playwright: {e}")
        return []

def scraping_directo_posiciones(url):
    """Nivel de respaldo 1: Scrapea la tabla HTML con limpieza agresiva."""
    print(f"  🔄 Scraping directo de tabla en {url}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,mp4}", lambda route: route.abort())
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector('table', timeout=5000)
            except PlaywrightTimeout:
                pass
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()
        
        soup = BeautifulSoup(html, 'html.parser')
        tablas = soup.find_all('table')
        
        for tabla in tablas:
            filas = tabla.find_all('tr')
            posiciones = []
            for fila in filas:
                columnas = fila.find_all(['td', 'th'])
                if len(columnas) >= 3:
                    # MEJORA 2: Saltar filas de encabezado
                    if all(col.name == 'th' for col in columnas):
                        continue
                        
                    # Limpieza agresiva de espacios raros (\xa0, etc.)
                    nombre = re.sub(r'[\xa0\s]+', ' ', columnas[1].get_text(strip=True))
                    
                    if any(eq in nombre.lower() for eq in EQUIPOS_LVBP):
                        ganados = re.sub(r'[^\d]', '', columnas[2].get_text(strip=True)) or '0'
                        perdidos = re.sub(r'[^\d]', '', columnas[3].get_text(strip=True)) or '0'
                        pct = columnas[4].get_text(strip=True) if len(columnas) > 4 else '.000'
                        # Limpiar el pct de caracteres no numéricos si es necesario
                        pct = re.sub(r'[^\d\.]', '', pct) or '.000'
                        posiciones.append(f"• {nombre}: {ganados} G - {perdidos} P ({pct})")
            
            if len(posiciones) >= 4:
                return "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
        return None
    except Exception as e:
        print(f"  ⚠️ Error en scraping directo de posiciones: {e}")
        return None

def scraping_directo_resultados(url):
    """Nivel de respaldo 2: Scrapea resultados con mayor precisión."""
    print(f"  🔄 Scraping directo de resultados...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,mp4}", lambda route: route.abort())
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector('.game, .match, .result, .boxscore, table', timeout=5000)
            except PlaywrightTimeout:
                pass
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()
        
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []
        
        # Buscamos bloques de texto que contengan equipos y palabras clave de resultado
        for elem in soup.find_all(['div', 'tr', 'li', 'td'], class_=re.compile(r'game|match|result|score|juego|resultado|boxscore|team', re.I)):
            texto = re.sub(r'\s+', ' ', elem.get_text(' ', strip=True))
            texto_lower = texto.lower()
            
            # MEJORA 3: Verificar que tenga equipos Y sea un resultado (final, ganó, perdió, marcador)
            tiene_equipo = any(eq in texto_lower for eq in EQUIPOS_LVBP)
            es_resultado = any(k in texto_lower for k in ['final', 'ganó', 'perdio', 'perdió', 'marcador', 'score', 'vs'])
            
            if tiene_equipo and es_resultado:
                # Extraer solo la parte relevante (primeras 120 letras para evitar bloques gigantes)
                resultados.append(texto[:120])
        
        if resultados:
            # Eliminar duplicados manteniendo el orden
            resultados_unicos = list(dict.fromkeys(resultados))[:5]
            return "📊 <b>RESULTADOS RECIENTES</b>\n\n" + "\n".join(resultados_unicos)
        
        # MEJORA 4: Manejo de temporada baja
        return "📅 <b>INFO LVBP</b>\n\nNo hay resultados de juegos recientes disponibles en este momento. ¡La temporada está en pausa o por comenzar!"
        
    except Exception as e:
        print(f"  ⚠️ Error en scraping directo de resultados: {e}")
        return None

def extraer_posiciones(datos_capturados):
    for dato in datos_capturados:
        if dato.get('type') == 'json':
            data = dato.get('data', {})
            if isinstance(data, dict):
                for key in ['standings', 'posiciones', 'tabla', 'data', 'results', 'teams', 'standings_entries', 'stats']:
                    if key in data:
                        equipos = data[key]
                        if isinstance(equipos, list) and len(equipos) >= 4:
                            return formatear_posiciones(equipos)
                
                for key, value in data.items():
                    if isinstance(value, list) and len(value) >= 4:
                        primer_item = value[0]
                        if isinstance(primer_item, dict):
                            claves = str(primer_item.keys()).lower()
                            if any(eq in claves for eq in ['team', 'equipo', 'name', 'nombre', 'wins', 'ganados', 'losses']):
                                return formatear_posiciones(value)
            elif isinstance(data, list) and len(data) >= 4:
                return formatear_posiciones(data)
    return None

def formatear_posiciones(equipos):
    posiciones = []
    for i, equipo in enumerate(equipos[:8], 1):
        if isinstance(equipo, dict):
            nombre = (equipo.get('team', {}).get('displayName', '') or 
                     equipo.get('equipo', '') or 
                     equipo.get('name', '') or 
                     equipo.get('nombre', '') or
                     str(equipo.get('team', '')))
            
            ganados = str(equipo.get('wins', equipo.get('ganados', equipo.get('w', '0'))))
            perdidos = str(equipo.get('losses', equipo.get('perdidos', equipo.get('l', '0'))))
            pct = str(equipo.get('pct', equipo.get('porcentaje', '.000')))
            
            if nombre and any(eq in str(nombre).lower() for eq in EQUIPOS_LVBP):
                posiciones.append(f"{i}. {nombre}: {ganados} G - {perdidos} P ({pct})")
    
    if len(posiciones) >= 4:
        return "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
    return None

def obtener_tabla_posiciones():
    print("  📊 Buscando tabla de posiciones...")
    
    datos = capturar_api_con_playwright(LVBP_POSICIONES)
    if datos:
        posiciones = extraer_posiciones(datos)
        if posiciones: return posiciones
    
    print("  🔄 Intentando scraping directo de posiciones...")
    posiciones = scraping_directo_posiciones(LVBP_POSICIONES)
    if posiciones: return posiciones
    
    print("  🔄 Intentando con página de resultados...")
    datos = capturar_api_con_playwright(LVBP_RESULTADOS)
    if datos:
        posiciones = extraer_posiciones(datos)
        if posiciones: return posiciones
    
    posiciones = scraping_directo_posiciones(LVBP_RESULTADOS)
    if posiciones: return posiciones
    
    return "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n⚠️ No se pudo extraer la tabla en este momento. Intenta más tarde."

def obtener_resultados_recientes():
    print("  📊 Buscando resultados del día...")
    
    resultados = scraping_directo_resultados(LVBP_RESULTADOS)
    if resultados:
        return resultados
    
    return "📅 <b>INFO LVBP</b>\n\nNo hay juegos programados o finalizados para hoy."
