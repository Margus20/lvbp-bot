# main.py
import os
import json
import requests
import time  # 🆕 Agregado para la pausa entre publicidades
from config import TOKEN, CANAL
# 🆕 Cambiado 'publicidad' por 'ppublicidad'
from extractores import resultados, posiciones, noticias, calendario, estadisticas, ppublicidad

VISTOS_FILE = 'vistos.json'

def cargar_vistos():
    """Carga el historial o lo repara automáticamente si tiene el formato viejo."""
    if os.path.exists(VISTOS_FILE):
        try:
            with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
                # BLINDAJE: Si son texto (formato viejo), los convertimos en lista
                if "resultados" not in datos or isinstance(datos["resultados"], str):
                    datos["resultados"] = []
                if "noticias" not in datos or isinstance(datos["noticias"], str):
                    datos["noticias"] = []
                
                # Aseguramos que existan las otras claves
                if "posiciones" not in datos: datos["posiciones"] = ""
                if "calendario" not in datos: datos["calendario"] = ""
                if "estadisticas" not in datos: datos["estadisticas"] = ""
                if "publicidad" not in datos: datos["publicidad"] = ""
                
                return datos
        except Exception as e:
            print(f"⚠️ Error al leer vistos.json ({e}). Creando uno nuevo...")
            
    # Si no existe o hubo error, devolvemos la estructura correcta desde cero
    return {
        "resultados": [],
        "posiciones": "",
        "calendario": "",
        "noticias": [],
        "estadisticas": "",
        "publicidad": ""
    }

def guardar_vistos(vistos):
    with open(VISTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(vistos, f, ensure_ascii=False, indent=2)

def enviar_a_telegram(mensaje):
    """Envía solo texto al canal"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    datos = {
        "chat_id": CANAL,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    respuesta = requests.post(url, json=datos)
    return respuesta.status_code == 200

def enviar_imagen_a_telegram(imagen_bytes, mensaje):
    """Envía una imagen con texto (caption) al canal"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {'photo': imagen_bytes}
    datos = {
        'chat_id': CANAL,
        'caption': mensaje,
        'parse_mode': 'HTML'
    }
    respuesta = requests.post(url, files=files, data=datos)
    return respuesta.status_code == 200

def main():
    print("🤖 Iniciando Bot Modular LVBP...")
    print("=" * 50)
    
    # 1. Cargar historial
    vistos = cargar_vistos()
    
    # ==========================================
    # 2. PROCESAR RESULTADOS (CON IMAGEN)
    # ==========================================
    print("📡 Extrayendo resultados...")
    data_resultados = resultados.obtener_ultimo_resultado()
    if data_resultados:
        if data_resultados["id"] not in vistos["resultados"]:
            print("✅ ¡Nuevo resultado detectado! Publicando...")
            if "imagen" in data_resultados:
                exito = enviar_imagen_a_telegram(data_resultados["imagen"], data_resultados["mensaje"])
            else:
                exito = enviar_a_telegram(data_resultados["mensaje"])
            
            if exito:
                vistos["resultados"].append(data_resultados["id"])
                print("📤 Enviado a Telegram con éxito.")
    print("-" * 50)

    # ==========================================
    # 3. PROCESAR POSICIONES (CON IMAGEN)
    # ==========================================
    print("📡 Extrayendo posiciones...")
    data_posiciones = posiciones.obtener_tabla_posiciones()
    if data_posiciones:
        if data_posiciones["id"] != vistos.get("posiciones"):
            print("✅ ¡Posiciones actualizadas! Publicando...")
            if "imagen" in data_posiciones:
                exito = enviar_imagen_a_telegram(data_posiciones["imagen"], data_posiciones["mensaje"])
            else:
                exito = enviar_a_telegram(data_posiciones["mensaje"])
            
            if exito:
                vistos["posiciones"] = data_posiciones["id"]
                print("📤 Enviado a Telegram con éxito.")
    print("-" * 50)

    # ==========================================
    # 4. PROCESAR NOTICIAS (CON IMAGEN)
    # ==========================================
    print("📡 Extrayendo noticias...")
    data_noticias = noticias.obtener_ultima_noticia()
    if data_noticias:
        if data_noticias["id"] not in vistos["noticias"]:
            print("✅ ¡Nueva noticia detectada! Publicando...")
            if "imagen" in data_noticias:
                exito = enviar_imagen_a_telegram(data_noticias["imagen"], data_noticias["mensaje"])
            else:
                exito = enviar_a_telegram(data_noticias["mensaje"])
            
            if exito:
                vistos["noticias"].append(data_noticias["id"])
                print("📤 Enviado a Telegram con éxito.")
    print("-" * 50)

    # ==========================================
    # 5. PROCESAR CALENDARIO (CON IMAGEN)
    # ==========================================
    print("📡 Extrayendo calendario...")
    data_calendario = calendario.obtener_jornada_hoy()
    if data_calendario:
        if data_calendario["id"] != vistos.get("calendario"):
            print("✅ ¡Nueva jornada detectada! Publicando...")
            if "imagen" in data_calendario:
                exito = enviar_imagen_a_telegram(data_calendario["imagen"], data_calendario["mensaje"])
            else:
                exito = enviar_a_telegram(data_calendario["mensaje"])
            
            if exito:
                vistos["calendario"] = data_calendario["id"]
                print("📤 Enviado a Telegram con éxito.")
    print("-" * 50)

    # ==========================================
    # 6. PROCESAR ESTADÍSTICAS (TEXTO)
    # ==========================================
    print("📡 Extrayendo estadísticas...")
    data_estadisticas = estadisticas.obtener_lideres_estadisticas()
    if data_estadisticas:
        if data_estadisticas["id"] != vistos.get("estadisticas"):
            print("✅ ¡Estadísticas actualizadas! Publicando...")
            if enviar_a_telegram(data_estadisticas["mensaje"]):
                vistos["estadisticas"] = data_estadisticas["id"]
                print("📤 Enviado a Telegram con éxito.")
    print("-" * 50)

    # ==========================================
    # 7. PROCESAR PUBLICIDAD (TODAS LAS IMÁGENES) 🆕
    # ==========================================
    print("📡 Extrayendo publicidad...")
    lista_publicidades = ppublicidad.obtener_todas_las_publicidades()
    
    if lista_publicidades:
        print(f"✅ {len(lista_publicidades)} publicidades detectadas. Publicando...")
        for i, data_publicidad in enumerate(lista_publicidades, 1):
            print(f"   📢 Publicidad {i}/{len(lista_publicidades)}...")
            if "imagen" in data_publicidad:
                exito = enviar_imagen_a_telegram(data_publicidad["imagen"], data_publicidad["mensaje"])
            else:
                exito = enviar_a_telegram(data_publicidad["mensaje"])
            
            if exito:
                print(f"   ✅ Publicidad {i} enviada con éxito.")
            else:
                print(f"   ❌ Falló el envío de publicidad {i}.")
            
            # Pequeña pausa de 1 segundo para no saturar la API de Telegram
            time.sleep(1)
    else:
        print("⚠️ No se pudo extraer publicidad.")
    print("=" * 50)
    
    # 8. Guardar historial actualizado
    print("💾 Guardando historial (vistos.json)...")
    guardar_vistos(vistos)
    print("✅ Bot completado exitosamente.")

if __name__ == '__main__':
    main()
