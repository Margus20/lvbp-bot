# extractores/noticias.py
import requests
import json5
from config import URLS_DATOS, HEADERS, TU_PAGINA

def obtener_ultima_noticia():
    """Extrae la última noticia del archivo noticias.js"""
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
        
        # 4. Formatear mensaje
        mensaje = (
            f"📰 <b>{titulo}</b>\n\n"
            f"🏷️ {tag}\n"
            f"📅 {fecha}\n\n"
            f"{resumen[:250]}{'...' if len(resumen) > 250 else ''}\n\n"
            f"🔗 Leer más: {TU_PAGINA}"
        )
        
        # ID único: el título de la noticia
        id_unico = titulo.strip()
        
        return {"mensaje": mensaje, "id": id_unico}
        
    except Exception as e:
        print(f"❌ Error al extraer noticias: {e}")
        return None
