# main.py
import os
import json
import requests
import time
import random
from datetime import datetime
from config import TOKEN, CANAL

# Extractores (traen los datos de tu web)
from extractores import resultados, posiciones, noticias, calendario, estadisticas, ppublicidad

# 🆕 Generadores (crean las imágenes bonitas que acabamos de arreglar)
from generadores import imagen_resultado, imagen_calendario, imagen_posiciones

VISTOS_FILE = 'vistos.json'

def cargar_vistos():
    """Carga el historial o lo repara automáticamente."""
    if os.path.exists(VISTOS_FILE):
        try:
            with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                # Blindaje de formato
                for key in ["resultados", "noticias"]:
                    if key not in datos or isinstance(datos[key], str):
                        datos[key] = []
                for key in ["posiciones", "calendario", "estadisticas", "publicidad_ultima_fecha"]:
                    if key not in datos:
                        datos[key] = "" if key != "publicidad_ultima_fecha" else None
                return datos
        except Exception as e:
            print(f"⚠️ Error al leer vistos.json ({e}). Creando uno nuevo...")
            
    return {
        "resultados": [],
        "posiciones": "",
        "calendario": "",
        "noticias": [],
        "estadisticas": "",
        "publicidad_ultima_fecha": None
    }

def guardar_vistos(vistos):
    with open(VISTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(vistos, f, ensure_ascii=False, indent=2)

def enviar_imagen_a_telegram(imagen_bytes, mensaje):
    """Envía una imagen con texto (caption) al canal"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {'photo': ('resumen.jpg', imagen_bytes, 'image/png')}
    datos = {
        'chat_id': CANAL,
        'caption': mensaje,
        'parse_mode': 'HTML'
    }
    respuesta = requests.post(url, files=files, data=datos)
    return respuesta.status_code == 200

def enviar_texto_a_telegram(mensaje):
    """Envía solo texto al canal"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    datos = {
        "chat_id": CANAL,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    respuesta = requests.post(url, json=datos)
    return respuesta.status_code == 200

def main():
    print("🤖 Iniciando Bot Modular LVBP - Modo Resumen Diario...")
    print("=" * 50)
    
    vistos = cargar_vistos()
    fecha_hoy_str = datetime.now().strftime('%d de %B de %Y').capitalize()
    
    # ==========================================
    # 1. RECOPILAR TODOS LOS DATOS DEL DÍA
    # ==========================================
    print("📡 Extrayendo datos para el resumen diario...")
    
    # Intentamos obtener listas. Si el extractor devuelve un solo diccionario, lo convertimos en lista.
    datos_resultados = resultados.obtener_resultados_del_dia() # O obtener_ultimo_resultado()
    if isinstance(datos_resultados, dict): datos_resultados = [datos_resultados]
    
    datos_calendario = calendario.obtener_jornada_hoy()
    if isinstance(datos_calendario, dict): datos_calendario = [datos_calendario]
    
    datos_posiciones = posiciones.obtener_tabla_posiciones() # Debería devolver una lista de dicts
    
    datos_noticias = noticias.obtener_ultima_noticia()
    
    # ==========================================
    # 2. GENERAR LAS IMÁGENES CON LOS NUEVOS GENERADORES
    # ==========================================
    print("🎨 Generando tarjetas visuales...")
    
    img_resultados = None
    if datos_resultados:
        print("   - Generando tarjeta de Resultados...")
        img_resultados = imagen_resultado.crear_imagen_resultados(datos_resultados, fecha_hoy_str)
        
    img_calendario = None
    if datos_calendario:
        print("   - Generando tarjeta de Calendario...")
        img_calendario = imagen_calendario.crear_imagen_calendario(datos_calendario, fecha_hoy_str)
        
    img_posiciones = None
    if datos_posiciones and isinstance(datos_posiciones, list):
        print("   - Generando tarjeta de Posiciones...")
        img_posiciones = imagen_posiciones.crear_imagen_posiciones(datos_posiciones)

    # ==========================================
    # 3. CONSTRUIR EL MENSAJE DE RESUMEN (DIGEST)
    # ==========================================
    resumen_texto = f"⚾ <b>RESUMEN DIARIO LVBP</b> ⚾\n📅 {fecha_hoy_str}\n\n"
    
    if datos_resultados:
        resumen_texto += f"✅ <b>Resultados:</b> {len(datos_resultados)} juego(s) finalizado(s).\n"
    if datos_calendario:
        resumen_texto += f"🗓️ <b>Jornada:</b> {len(datos_calendario)} juego(s) programado(s).\n"
    if datos_noticias:
        resumen_texto += f"📰 <b>Noticia:</b> {datos_noticias.get('titulo', 'Nueva noticia disponible')}\n"
        
    resumen_texto += "\n👇 <i>Revisa las imágenes a continuación para ver los detalles completos.</i>"

    # ==========================================
    # 4. PUBLICAR EN TELEGRAM (ORDENADO)
    # ==========================================
    print("📤 Enviando resumen al canal...")
    
    # Enviamos la imagen más importante primero (Resultados o Calendario) con el texto resumen
    imagen_principal = img_resultados if img_resultados else img_calendario
    
    if imagen_principal:
        exito = enviar_imagen_a_telegram(imagen_principal, resumen_texto)
        if exito:
            print("   ✅ Imagen principal enviada.")
            time.sleep(1.5) # Pausa para no saturar
            
    # Enviamos las imágenes secundarias sin texto (o con texto mínimo)
    if img_calendario and img_calendario != imagen_principal:
        enviar_imagen_a_telegram(img_calendario, "🗓️ <b>Jornada del Día</b>")
        time.sleep(1.5)
        
    if img_posiciones:
        enviar_imagen_a_telegram(img_posiciones, "🏆 <b>Tabla de Posiciones</b>")
        time.sleep(1.5)

    # ==========================================
    # 5. PUBLICIDAD (CONTROLADA: 1 VEZ POR DÍA)
    # ==========================================
    print("📢 Revisando publicidad...")
    hoy_fecha = datetime.now().strftime('%Y-%m-%d')
    
    # Solo publicamos publicidad si NO hemos publicado hoy
    if vistos.get("publicidad_ultima_fecha") != hoy_fecha:
        lista_publicidades = ppublicidad.obtener_todas_las_publicidades()
        if lista_publicidades:
            # Elegimos 1 publicidad al azar para no ser repetitivos
            pub_elegida = random.choice(lista_publicidades)
            print(f"   - Enviando publicidad: {pub_elegida.get('mensaje', 'Anuncio')[:30]}...")
            
            if "imagen" in pub_elegida:
                enviar_imagen_a_telegram(pub_elegida["imagen"], pub_elegida["mensaje"])
            else:
                enviar_texto_a_telegram(pub_elegida["mensaje"])
                
            # Marcamos que ya publicamos publicidad hoy
            vistos["publicidad_ultima_fecha"] = hoy_fecha
            print("   ✅ Publicidad enviada (1 vez por día).")
    else:
        print("   ⏭️ Publicidad omitida (ya se publicó hoy).")

    # ==========================================
    # 6. ACTUALIZAR HISTORIAL
    # ==========================================
    print("💾 Guardando historial...")
    guardar_vistos(vistos)
    print("✅ Bot completado exitosamente. ¡Que viva el béisbol!")

if __name__ == '__main__':
    main()
