import requests
from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Nombres completos de los 8 equipos de la LVBP
EQUIPOS_LVBP = [
    'leones del caracas', 'navegantes del magallanes', 'tiburones de la guaira',
    'aguilas del zulia', 'tigres de aragua', 'caribes de anzoategui', 'caribes de anzoátegui',
    'cardenales de lara', 'bravos de margarita'
]

def obtener_tabla_posiciones():
    """Entra a la web de la LVBP con un navegador invisible y extrae la tabla."""
    print("  🕵️ Entrando a LVBP.com con navegador invisible...")
    try:
        with sync_playwright() as p:
            # Lanzamos el navegador en modo invisible (headless)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Entramos a la página y esperamos a que cargue todo
            page.goto("https://www.lvbp.com/posiciones/", wait_until="networkidle", timeout=20000)
            
            # Esperamos específicamente a que aparezca una tabla
            try:
                page.wait_for_selector("table", timeout=10000)
            except:
                print("  ⚠️ No se encontró tabla de posiciones.")
                browser.close()
                return None

            # Obtenemos el HTML completo ya renderizado
            html = page.content()
            browser.close()
            
        # Ahora usamos BeautifulSoup para leer ese HTML limpio
        soup = BeautifulSoup(html, 'html.parser')
        filas = soup.find_all('tr')
        
        posiciones = []
        for fila in filas:
            columnas = fila.find_all('td')
            if len(columnas) >= 4:
                nombre_equipo = columnas[1].get_text(strip=True).lower()
                # Verificamos si es un equipo de la LVBP
                if any(eq in nombre_equipo for eq in EQUIPOS_LVBP):
                    ganados = columnas[2].get_text(strip=True)
                    perdidos = columnas[3].get_text(strip=True)
                    pct = columnas[4].get_text(strip=True) if len(columnas) > 4 else ".000"
                    # Formateamos en lista vertical para tableta
                    posiciones.append(f"• {columnas[1].get_text(strip=True)}: {ganados} G - {perdidos} P ({pct})")
                    
        if len(posiciones) >= 4:
            return "🏆 <b>TABLA DE POSICIONES LVBP</b>\n\n" + "\n".join(posiciones)
            
    except Exception as e:
        print(f"  ️ Error con Playwright: {e}")
        
    return None

def obtener_resultados_recientes():
    """Busca en Meridiano el último resumen de resultados si la LVBP falla."""
    try:
        resp = requests.get("https://meridiano.net/beisbol/beisbol-venezolano/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|news|card', re.I))
        
        for art in articulos[:10]:
            titulo_tag = art.find(['h2', 'h3', 'a'])
            if titulo_tag:
                titulo = titulo_tag.get_text(strip=True).lower()
                if 'resultados' in titulo or 'jornada' in titulo or 'cerró' in titulo:
                    desc_tag = art.find('p')
                    enlace_tag = art.find('a', href=True)
                    enlace = enlace_tag['href'] if enlace_tag else "https://meridiano.net"
                    
                    if desc_tag:
                        texto = f"📊 <b>RESUMEN DE LA JORNADA</b>\n\n"
                        texto += f"{desc_tag.get_text(strip=True)[:250]}...\n\n"
                        texto += f"🔗 Lee más: {enlace}"
                        return texto
    except Exception:
        pass
    return None
