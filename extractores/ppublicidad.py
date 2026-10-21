# extractores/ppublicidad.py
import requests
import json5
from io import BytesIO
from config import HEADERS, TU_PAGINA

# URL directa a tu archivo que funciona en la página web
URL_PUBLICIDAD = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/js/datos/ppublicidad.js'

def obtener_todas_las_publicidades():
    """Extrae TODAS las publicidades del archivo ppublicidad.js y descarga sus imágenes"""
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URL_PUBLICIDAD, headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const PUBLICIDAD = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return []
        
        # 3. Lista para guardar TODAS las publicidades
        lista_publicidades = []
        
        for pub in datos:
            imagen_url = pub.get('imagen', '')
            alt_text = pub.get('alt', 'Publicidad')
            
            # 4. Mensaje mejorado con etiqueta clara de "Publicidad"
            mensaje = (
                f"📢 <b>PUBLICIDAD</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{alt_text}\n\n"
                f"🔗 Visita nuestro canal: {TU_PAGINA}\n\n"
                f"<i>Este es un mensaje publicitario de LVBP al Día</i>"
            )
            
            # 5. Descargar la imagen original tal cual está
            imagen_bytes = None
            if imagen_url and imagen_url.startswith('http'):
                try:
                    resp_img = requests.get(imagen_url, headers=HEADERS, timeout=10)
                    if resp_img.status_code == 200 and len(resp_img.content) > 1000:
                        imagen_bytes = BytesIO(resp_img.content)
                except:
                    pass
            
            # ID único: la URL de la imagen
            id_unico = imagen_url.strip()
            
            # 6. Agregar a la lista
            resultado = {"mensaje": mensaje, "id": id_unico}
            if imagen_bytes:
                resultado["imagen"] = imagen_bytes
                
            lista_publicidades.append(resultado)
            
        return lista_publicidades
        
    except Exception as e:
        print(f"❌ Error al extraer publicidad: {e}")
        return []
