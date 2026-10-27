# extractores/estadisticas.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_lideres_estadisticas():
    """
    Extrae TODOS los líderes estadísticos del archivo lideres.js
    y los devuelve en un formato que el generador pueda usar.
    """
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['lideres'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const LIDERES = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, dict):
            return None
        
        # 3. Formatear mensaje de texto (resumen)
        mensaje = "📊 <b>LÍDERES ESTADÍSTICOS LVBP</b>\n\n"
        
        categorias_resumen = {
            'hr': '💥 Jonrones',
            'average': '🏏 Average',
            'ci': '🎯 Carreras Impulsadas',
            'era': ' Efectividad',
            'hits': '📈 Hits'
        }
        
        for cat_key, cat_nombre in categorias_resumen.items():
            if cat_key in datos and datos[cat_key]:
                lider = datos[cat_key][0]
                mensaje += f"{cat_nombre}: <b>{lider.get('nombre')}</b> ({lider.get('valor')})\n"
        
        mensaje += f"\n🔗 Ver estadísticas completas: {TU_PAGINA}#estadisticas"
        
        # 4. ID único basado en los líderes principales
        id_unico = f"ESTADISTICAS_{datos.get('hr', [{}])[0].get('nombre', '')}"
        
        return {
            "mensaje": mensaje, 
            "id": id_unico,
            "datos_completos": datos  # Para que el generador cree la imagen
        }
        
    except Exception as e:
        print(f"❌ Error al extraer estadísticas: {e}")
        return None
