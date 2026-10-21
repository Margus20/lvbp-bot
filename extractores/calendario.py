# extractores/calendario.py
import requests
import json5
from datetime import datetime
from config import URLS_DATOS, HEADERS, TU_PAGINA
from generadores.imagen_calendario import crear_imagen_calendario  # 🆕 NUEVA LÍNEA

def obtener_jornada_hoy():
    """Extrae los juegos de hoy del archivo calendario.js y genera su imagen"""
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['calendario'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const CALENDARIO = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return None
        
        # 3. Filtrar juegos de hoy (o los primeros si no hay fecha exacta)
        hoy = datetime.now().strftime('%d %b %Y').upper()
        juegos_hoy = [j for j in datos if hoy in j.get('fecha', '').upper()]
        
        # Si no hay juegos con fecha de hoy, tomar los primeros 3
        if not juegos_hoy:
            juegos_hoy = datos[:3]
        
        # 4. Formatear mensaje
        fecha_hoy = datetime.now().strftime('%d de %B').capitalize()
        mensaje = f"📅 <b>JORNADA DE HOY - {fecha_hoy}</b>\n\n"
        
        for juego in juegos_hoy:
            visitante = juego.get('visitante', '???')
            local = juego.get('local', '???')
            hora = juego.get('hora', 'Por definir')
            transmision = juego.get('transmision', '')
            lugar = juego.get('lugar', '')
            
            mensaje += f"⚾ {hora} - {visitante} vs {local}\n"
            if lugar:
                mensaje += f"   🏟️ {lugar}\n"
            if transmision and transmision != 'Por definir':
                mensaje += f"   📺 {transmision}\n"
            mensaje += "\n"
        
        mensaje += f"🔗 Ver calendario completo: {TU_PAGINA}#calendario"
        
        # 5.  GENERAR LA IMAGEN VERTICAL BLANCA
        imagen_bytes = crear_imagen_calendario(juegos_hoy, fecha_hoy)
        
        # ID único: fecha + cantidad de juegos
        id_unico = f"{fecha_hoy}_{len(juegos_hoy)}"
        
        # 6. 🆕 Devolver mensaje, ID y la imagen
        return {
            "mensaje": mensaje, 
            "id": id_unico,
            "imagen": imagen_bytes
        }
        
    except Exception as e:
        print(f"❌ Error al extraer calendario: {e}")
        return None
