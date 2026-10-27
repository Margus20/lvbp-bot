# extractores/estadisticas.py
import requests
import json5
import re
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_lideres_estadisticas():
    """
    Extrae los líderes estadísticos del archivo lideres.js de forma robusta,
    ignorando comas extra o código adicional (como MASCOTAS).
    """
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['lideres'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        texto_js = respuesta.text
        
        # 2. Extraer SOLO el contenido del objeto LIDERES usando Regex
        # Busca desde "export const LIDERES = {" hasta el último "}" antes de "export const MASCOTAS"
        match = re.search(r'export const LIDERES = (\{.*?\})\s*;', texto_js, re.DOTALL)
        
        if not match:
            print("❌ No se pudo encontrar el bloque LIDERES en el archivo.")
            return None
            
        texto_limpio = match.group(1)
        
        # 3. Parsear con json5
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, dict):
            print("❌ Los datos de líderes no son un diccionario válido.")
            return None
        
        # 4. Formatear mensaje de texto (resumen)
        mensaje = "📊 <b>LÍDERES ESTADÍSTICOS LVBP</b>\n\n"
        
        # Usamos las claves exactas de tu archivo lideres.js
        categorias_resumen = {
            'jonrones': '💥 Jonrones',
            'average': '🏏 Average',
            'impulsadas': '🎯 Carreras Impulsadas',
            'efectividad': '🎯 Efectividad',
            'hits': '📈 Hits'
        }
        
        for cat_key, cat_nombre in categorias_resumen.items():
            if cat_key in datos and datos[cat_key]:
                lider = datos[cat_key][0]
                nombre = lider.get('nombre', 'Desconocido')
                valor = lider.get('valor', '0')
                mensaje += f"{cat_nombre}: <b>{nombre}</b> ({valor})\n"
        
        mensaje += f"\n🔗 Ver estadísticas completas: {TU_PAGINA}#estadisticas"
        
        # 5. ID único para control
        primer_lider = ""
        if 'jonrones' in datos and datos['jonrones']:
            primer_lider = datos['jonrones'][0].get('nombre', '')
        id_unico = f"ESTADISTICAS_{primer_lider}"
        
        return {
            "mensaje": mensaje, 
            "id": id_unico,
            "datos_completos": datos  # Se pasa todo el diccionario al generador
        }
        
    except Exception as e:
        print(f"❌ Error al extraer estadísticas: {e}")
        return None
