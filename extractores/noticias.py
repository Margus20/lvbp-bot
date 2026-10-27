# extractores/noticias.py
import requests
import json5
from io import BytesIO
from config import URLS_DATOS, HEADERS, TU_PAGINA

# URL base de tu repositorio para convertir rutas relativas en absolutas
REPO_BASE = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/'

def obtener_todas_las_noticias():
    """
    Extrae TODAS las noticias disponibles en el archivo noticias.js.
    Devuelve una lista con cada noticia: título, imagen real y enlace.
    SIN descripción ni resumen, tal como se solicitó.
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
        
        # Recorremos las noticias (máximo 5 para no saturar)
        for noticia in datos[:5]: 
            titulo = noticia.get('titulo', 'Sin título')
            fecha = noticia.get('fecha', '')
            imagen_rel = noticia.get('imagen', '')
            
            # 1. CORRECCIÓN DE IMAGEN: Construir URL absoluta si es relativa
            if imagen_rel and not imagen_rel.startswith('http'):
                imagen_url = REPO_BASE + imagen_rel
            else:
                imagen_url = imagen_rel
            
            # 2. MENSAJE LIMPIO: Solo título, fecha y enlace (sin resumen)
            mensaje = (
                f"📰 <b>{titulo}</b>\n"
                f"📅 {fecha}\n\n"
                f"🔗 <b>Leer noticia completa:</b> {TU_PAGINA}"
            )
            
            # Descargar la imagen real de la noticia
            imagen_bytes = None
            if imagen_url:
                try:
                    resp_img = requests.get(imagen_url, headers=HEADERS, timeout=10)
                    if resp_img.status_code == 200 and len(resp_img.content) > 1000:
                        imagen_bytes = BytesIO(resp_img.content)
                except Exception as img_err:
                    print(f"⚠️ No se pudo descargar imagen de '{titulo}': {img_err}")
            
            # ID único para control de duplicados
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

# Compatibilidad con funciones que esperen un solo resultado
def obtener_ultima_noticia():
    noticias = obtener_todas_las_noticias()
    return noticias[0] if noticias else None
