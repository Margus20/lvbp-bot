# extractores/noticias.py
import requests
import json5
from io import BytesIO  # 🆕 Agregado para manejar la imagen en memoria
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_ultima_noticia():
    """Extrae la última noticia del archivo noticias.js y su imagen"""
    try:
        # 1. Descargar el archivo JS
        respuesta = requests.get(URLS_DATOS['noticias'], headers=HEADERS, timeout=10)
        respuesta.raise_for_status()
        
        # 2. Parsear con json5
        texto_js = respuesta.text
        texto_limpio = texto_js.replace('export const NOTICIAS = ', '').strip().rstrip(';')
        datos = json5.loads(texto_limpio)
        
        if not datos:
            return None
        
        # 3. Tomar la última noticia (la más reciente)
        noticia = datos[-1]
        
        titulo = noticia.get('titulo', 'Sin título')
        tag = noticia.get('tag', 'LVBP')
        fecha = noticia.get('fecha', '')
        resumen = noticia.get('resumen', '')
        imagen_url = noticia.get('imagen', '')  # 🆕 Obtenemos la URL de la imagen
        
        # 4. Formatear mensaje
        mensaje = (
            f"📰 <b>{titulo}</b>\n\n"
            f"🏷️ {tag}\n"
            f"📅 {fecha}\n\n"
            f"{resumen[:250]}{'...' if len(resumen) > 250 else ''}\n\n"
            f"🔗 Leer más: {TU_PAGINA}"
        )
        
        # 5. 🆕 Descargar la imagen de la noticia (si existe)
        imagen_bytes = None
        if imagen_url and imagen_url.startswith('http'):
            try:
                resp_img = requests.get(imagen_url, headers=HEADERS, timeout=10)
                if resp_img.status_code == 200 and len(resp_img.content) > 1000:
                    imagen_bytes = BytesIO(resp_img.content)
            except:
                pass # Si falla la descarga, se enviará solo el texto (no rompe el bot)
        
        # ID único: el título de la noticia
        id_unico = titulo.strip()
        
        # 6. 🆕 Devolver mensaje, ID y la imagen (si se pudo descargar)
        resultado = {"mensaje": mensaje, "id": id_unico}
        if imagen_bytes:
            resultado["imagen"] = imagen_bytes
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error al extraer noticias: {e}")
        return None
