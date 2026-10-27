# extractores/posiciones.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_tabla_posiciones():
    """
    Extrae la tabla de posiciones del archivo posiciones.js.
    Devuelve la LISTA de equipos para que el generador cree la imagen.
    """
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['posiciones'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const POSICIONES = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, list):
            print("❌ No hay datos de posiciones o formato incorrecto")
            return None
        
        # 3. Devolver la lista de equipos directamente
        # Cada equipo debe tener: nombre, jj, jg, jp, pct, dif, racha
        return datos
        
    except Exception as e:
        print(f"❌ Error al extraer posiciones: {e}")
        return None
