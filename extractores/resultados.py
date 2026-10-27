# extractores/resultados.py
import requests
import json5
from config import URLS_DATOS, HEADERS

def obtener_resultados_del_dia():
    """
    Extrae TODOS los resultados de la jornada más reciente del archivo resultados.js.
    Devuelve una lista de diccionarios con los datos limpios para que el generador 
    cree la tarjeta con todos los juegos del día.
    """
    try:
        # 1. Descargamos el archivo JS crudo
        respuesta = requests.get(URLS_DATOS['resultados'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. json5 convierte el texto "export const RESULTADOS = [...]" en una lista de Python
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const RESULTADOS = ', '').strip().rstrip(';')
        
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, list):
            return []
            
        # 3. Identificamos la fecha del último juego (la jornada más reciente)
        fecha_mas_reciente = datos[-1].get('fecha', '')
        
        # 4. Filtramos y devolvemos TODOS los juegos que coincidan con esa fecha
        juegos_del_dia = [juego for juego in datos if juego.get('fecha') == fecha_mas_reciente]
        
        # Fallback: si no hay fecha, devolvemos los últimos 4 juegos por seguridad
        if not juegos_del_dia:
            juegos_del_dia = datos[-4:]
            
        return juegos_del_dia
        
    except Exception as e:
        print(f"❌ Error al extraer resultados: {e}")
        return []

def obtener_ultimo_resultado():
    """
    Mantiene compatibilidad por si se usa en otro script.
    Devuelve solo el último juego de la lista.
    """
    resultados = obtener_resultados_del_dia()
    if resultados:
        return resultados[-1]
    return None
