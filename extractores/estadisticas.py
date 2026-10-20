# extractores/estadisticas.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_lideres_estadisticas():
    """Extrae los líderes estadísticos del archivo lideres.js"""
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['lideres'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const LIDERES = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return None
        
        # 3. Formatear mensaje
        mensaje = "📊 <b>LÍDERES ESTADÍSTICOS LVBP</b>\n\n"
        
        # Carreras Anotadas
        if 'carreras' in datos and datos['carreras']:
            lider_carreras = datos['carreras'][0]
            mensaje += (
                f"🏃 <b>CARRERAS:</b>\n"
                f"   {lider_carreras.get('nombre')} ({lider_carreras.get('valor')})\n\n"
            )
        
        # Average de Bateo
        if 'average' in datos and datos['average']:
            lider_average = datos['average'][0]
            mensaje += (
                f"🏏 <b>AVERAGE:</b>\n"
                f"   {lider_average.get('nombre')} ({lider_average.get('valor')})\n\n"
            )
        
        # Jonrones
        if 'hr' in datos and datos['hr']:
            lider_hr = datos['hr'][0]
            mensaje += (
                f"💥 <b>JONRONES:</b>\n"
                f"   {lider_hr.get('nombre')} ({lider_hr.get('valor')})\n\n"
            )
        
        # Efectividad (Pitchers)
        if 'era' in datos and datos['era']:
            lider_era = datos['era'][0]
            mensaje += (
                f"🎯 <b>EFECTIVIDAD:</b>\n"
                f"   {lider_era.get('nombre')} ({lider_era.get('valor')})\n\n"
            )
        
        mensaje += f"🔗 Ver estadísticas completas: {TU_PAGINA}#estadisticas"
        
        # ID único: combinamos los nombres de los líderes
        id_unico = f"{datos.get('carreras', [{}])[0].get('nombre', '')}_ERA"
        
        return {"mensaje": mensaje, "id": id_unico}
        
    except Exception as e:
        print(f"❌ Error al extraer estadísticas: {e}")
        return None
