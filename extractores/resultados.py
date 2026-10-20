# extractores/resultados.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_ultimo_resultado():
    """Extrae el último resultado del archivo resultados.js"""
    try:
        # 1. Descargamos el archivo JS crudo
        respuesta = requests.get(URLS_DATOS['resultados'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. json5 convierte el texto "export const RESULTADOS = [...]" en una lista de Python
        texto_js = respuesta.text
        # Truco: json5 a veces falla con "export const", así que lo limpiamos
        texto_limpio = texto_js.replace('export const RESULTADOS = ', '').strip().rstrip(';')
        
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return None
            
        # 3. Tomamos el último juego de la lista
        ultimo_juego = datos[-1]
        
        # 4. Formateamos el mensaje para Telegram
        visitante = ultimo_juego.get('visitante', '???')
        local = ultimo_juego.get('local', '???')
        score_vis = ultimo_juego.get('scoreVisitante', 0)
        score_loc = ultimo_juego.get('scoreLocal', 0)
        fecha = ultimo_juego.get('fecha', '')
        
        mensaje = (
            f"⚾ <b>RESULTADO FINAL</b>\n\n"
            f"🏟️ {visitante} <b>{score_vis}</b> - <b>{score_loc}</b> {local}\n"
            f"📅 {fecha}\n\n"
            f"🔗 Ver detalles: {TU_PAGINA}#resultados"
        )
        
        # Devolvemos el mensaje y un "ID único" (la fecha + equipos) para saber si ya se publicó
        id_unico = f"{fecha}_{visitante}_{local}"
        return {"mensaje": mensaje, "id": id_unico}
        
    except Exception as e:
        print(f"❌ Error al extraer resultados: {e}")
        return None
