# extractores/posiciones.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_tabla_posiciones():
    """Extrae la tabla de posiciones del archivo posiciones.js"""
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['posiciones'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const POSICIONES = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return None
        
        # 3. Formatear mensaje
        mensaje = " <b>TABLA DE POSICIONES LVBP</b>\n\n"
        
        for i, equipo in enumerate(datos, 1):
            nombre = equipo.get('nombre', '???')
            # Acortar nombres largos
            nombre_corto = (nombre
                .replace(' de Anzoátegui', '')
                .replace(' de Aragua', '')
                .replace(' de Lara', '')
                .replace(' de Margarita', '')
                .replace(' del Zulia', '')
                .replace(' de La Guaira', '')
                .replace(' del Caracas', '')
                .replace(' del Magallanes', '')
            )
            
            jj = equipo.get('jj', 0)
            jg = equipo.get('jg', 0)
            jp = equipo.get('jp', 0)
            racha = equipo.get('racha', '')
            
            # Emoji según racha
            emoji_racha = "🟢" if "G" in racha else "🔴"
            
            mensaje += (
                f"{i}. <b>{nombre_corto}</b>\n"
                f"   JJ: {jj} | G: {jg} | P: {jp} {emoji_racha} {racha}\n\n"
            )
        
        mensaje += f"🔗 Ver tabla completa: {TU_PAGINA}#posiciones"
        
        # ID único: usamos el primer equipo + su racha para detectar cambios
        id_unico = f"{datos[0].get('nombre')}_{datos[0].get('racha')}" if datos else ""
        
        return {"mensaje": mensaje, "id": id_unico}
        
    except Exception as e:
        print(f"❌ Error al extraer posiciones: {e}")
        return None
