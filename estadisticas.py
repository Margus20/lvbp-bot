import requests
import json
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

LVBP_RESULTADOS = "https://stats.lvbp.com/resultados.php"
LVBP_POSICIONES = "https://stats.lvbp.com/posiciones.php"

EQUIPOS_LVBP = [
    'leones del caracas', 'navegantes del magallanes', 'tiburones de la guaira',
    'aguilas del zulia', 'tigres de aragua', 'caribes de anzoategui',
    'cardenales de lara', 'bravos de margarita'
]

def capturar_api_con_playwright(url):
    print(f"  🕵️ Interceptando red en {url}...")
    datos_capturados = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            def handle_response(response):
                if 'lvbp' in response.url.lower() and response.status == 200:
                    try:
                        body = response.json()
                        datos_capturados.append({
                            'url': response.url,
                            'data': body
                        })
                        print(f"  ✅ API capturada: {response.url}")
                    except:
                        pass
            
            page.on("response", handle_response)
            # CAMBIO CLAVE: domcontentloaded + timeout mayor
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)
            browser.close()
            
        return datos_capturados
        
    except Exception as e:
        print(f"  ⚠️ Error con Playwright: {e}")
        return []

def extraer_posiciones(datos_capturados):
    for dato in datos_capturados:
        data = dato.get('data', {})
        
        if isinstance(data, dict):
            for key in ['standings', 'posiciones', 'tabla', 'data', 'results', 'teams']:
                if key in data:
                    equipos = data[key]
                    if isinstance(equipos, list) and len(equipos) >= 4:
                        return formatear_posiciones(equipos)
            
            for key, value in data.items():
                if isinstance(value, list) and len(value) >= 4:
                    primer_item = value[0]
                    if isinstance(primer_item, dict):
                        claves = str(primer_item.keys()).lower()
                        if any(eq in claves for eq in ['team', 'equipo', 'name', 'nombre', 'wins', 'ganados', 'losses', 'perdidos']):
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
            
            ganados = equipo.get('wins', equipo.get('ganados', equipo.get('w', '0')))
            perdidos = equipo.get('losses', equipo.get('perdidos', equipo.get('l', '0')))
            pct = equipo.get('pct', equipo.get('porcentaje', '.000'))
            
            if nombre and any(eq in str(nombre).lower() for eq in EQUIPOS_LVBP):
                posiciones.append(f"{i}. {nombre}: {ganados}G - {perdidos}P ({pct})")
    
    if len(posiciones) >= 4:
        return "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
    
    return None

def extraer_resultados(datos_capturados):
    for dato in datos_capturados:
        data = dato.get('data', {})
        
        if isinstance(data, dict):
            for key in ['games', 'resultados', 'scores', 'events', 'data']:
                if key in data:
                    juegos = data[key]
                    if isinstance(juegos, list) and len(juegos) > 0:
                        return formatear_resultados(juegos)
            
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    primer_item = value[0]
                    if isinstance(primer_item, dict):
                        claves = str(primer_item.keys()).lower()
                        if any(k in claves for k in ['home', 'away', 'local', 'visitante', 'score', 'resultado']):
                            return formatear_resultados(value)
        
        elif isinstance(data, list) and len(data) > 0:
            return formatear_resultados(data)
    
    return None

def formatear_resultados(juegos):
    resultados = []
    
    for juego in juegos[:5]:
        if isinstance(juego, dict):
            local = (juego.get('home', {}).get('team', {}).get('displayName', '') or
                    juego.get('local', {}).get('nombre', '') or
                    juego.get('homeTeam', ''))
            
            visitante = (juego.get('away', {}).get('team', {}).get('displayName', '') or
                        juego.get('visitante', {}).get('nombre', '') or
                        juego.get('awayTeam', ''))
            
            score_local = juego.get('home', {}).get('score', juego.get('scoreHome', '0'))
            score_visitante = juego.get('away', {}).get('score', juego.get('scoreAway', '0'))
            
            estado = juego.get('status', {}).get('type', {}).get('state', 'final')
            
            if local and visitante:
                if estado == 'post' or estado == 'final':
                    resultados.append(f"⚾ {local} <b>{score_local}</b> - <b>{score_visitante}</b> {visitante}")
                else:
                    resultados.append(f" {local} vs {visitante} ({estado})")
    
    if resultados:
        return "📊 <b>RESULTADOS DE HOY</b>\n\n" + "\n".join(resultados)
    
    return None

def obtener_tabla_posiciones():
    print("  📊 Buscando tabla de posiciones...")
    datos = capturar_api_con_playwright(LVBP_POSICIONES)
    
    if datos:
        posiciones = extraer_posiciones(datos)
        if posiciones:
            return posiciones
    
    print("  🔄 Intentando con página de resultados...")
    datos = capturar_api_con_playwright(LVBP_RESULTADOS)
    
    if datos:
        posiciones = extraer_posiciones(datos)
        if posiciones:
            return posiciones
    
    return None

def obtener_resultados_recientes():
    print("  📊 Buscando resultados del día...")
    datos = capturar_api_con_playwright(LVBP_RESULTADOS)
    
    if datos:
        resultados = extraer_resultados(datos)
        if resultados:
            return resultados
    
    return None
