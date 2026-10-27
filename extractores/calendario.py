# extractores/calendario.py
import requests
import json5
from datetime import datetime
from config import URLS_DATOS, HEADERS

def obtener_jornada_hoy():
    """
    Extrae los juegos de la jornada más reciente (hoy o próximos) del archivo calendario.js.
    Devuelve una lista de diccionarios con los datos limpios para que el generador 
    cree la tarjeta vertical con todos los juegos del día.
    """
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['calendario'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const CALENDARIO = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, list):
            return []
        
        # 3. Filtrar juegos de hoy
        # Formato esperado en tu JS: '27 Oct 2026' -> lo convertimos a mayúsculas para comparar
        hoy_str = datetime.now().strftime('%d %b %Y').upper() 
        
        juegos_hoy = [j for j in datos if hoy_str in j.get('fecha', '').upper()]
        
        # 4. Fallback inteligente: Si no hay juegos con fecha de hoy (ej: es de madrugada o día libre)
        if not juegos_hoy:
            # Buscamos los próximos juegos que NO estén finalizados
            juegos_pendientes = [j for j in datos if not j.get('finalizado', False)]
            if juegos_pendientes:
                juegos_hoy = juegos_pendientes[:4] # Tomamos los próximos 4
            else:
                # Si todo está finalizado, tomamos los últimos 3 registrados como referencia
                juegos_hoy = datos[-3:]
            
        return juegos_hoy
        
    except Exception as e:
        print(f"❌ Error al extraer calendario: {e}")
        return []

def obtener_ultimo_juego_compatibilidad():
    """
    Mantiene compatibilidad por si se usa en otro script que espere un solo diccionario.
    """
    juegos = obtener_jornada_hoy()
    if juegos:
        return juegos[0]
    return None
