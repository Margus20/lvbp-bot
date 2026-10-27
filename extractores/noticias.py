# extractores/noticias.py
import requests
import json5
from io import BytesIO
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_todas_las_noticias():
    """
    Extrae TODAS las noticias disponibles en el archivo noticias.js.
    Devuelve una lista con cada noticia, su imagen real y su enlace.
    """
    try:
        respuesta = requests.get(URLS_DATOS['noticias'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const NOTICIAS = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos or not isinstance(datos, list):
            return []
        
        lista_noticias = []
        
        # Recorremos todas las noticias (o las primeras 5 para no saturar)
        for noticia in datos[:5]: 
            titulo = noticia.get('titulo', 'Sin título')
            fecha = noticia.get('fecha', '')
            imagen_url = noticia.get('imagen', '')
            
            # Creamos un resumen corto desde el contenido HTML
            contenido_crudo = noticia.get('contenido', '')
            resumen_limpio = contenido_crudo.replace('<p>', '').replace('</p>', ' ').replace('<strong>', '').replace('</strong>', '')
            resumen_corto = resumen_limpio[:150] + ('...' if len(resumen_limpio) > 150 else '')
            
            # Mensaje con enlace directo a la página
            mensaje = (
                f"📰 <b>{titulo}</b>\n"
                f"📅 {fecha}\n\n"
                f"{resumen_corto}\n\n"
                f"🔗 <b>Leer noticia completa:</b> {TU_PAGINA}"
            )
            
            # Descargar la imagen real de la noticia
            imagen_bytes = None
            if imagen_url and imagen_url.startswith('http'):
                try:
                    resp_img = requests.get(imagen_url, headers=HEADERS, timeout=10)
                    if resp_img.status_code == 200 and len(resp_img.content) > 1000:
                        imagen_bytes = BytesIO(resp_img.content)
                except:
                    pass
            
            # ID único para control
            id_unico = f"{titulo.strip()}_{fecha}".replace(" ", "_")
            
            lista_noticias.append({
                "mensaje": mensaje, 
                "id": id_unico,
                "imagen": imagen_bytes
            })
            
        return lista_noticias
        
    except Exception as e:
        print(f"❌ Error al extraer noticias: {e}")
        return []

# Compatibilidad
def obtener_ultima_noticia():
    noticias = obtener_todas_las_noticias()
    return noticias[0] if noticias else None
