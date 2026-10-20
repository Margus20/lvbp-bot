# main.py
import os
import json
import requests
from config import TOKEN, CANAL
# Agregamos las importaciones de los nuevos extractores
from extractores import resultados, posiciones, noticias, calendario, estadisticas

VISTOS_FILE = 'vistos.json'

def cargar_vistos():
    """Carga el historial o lo repara automáticamente si tiene el formato viejo."""
    if os.path.exists(VISTOS_FILE):
        try:
            with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
                # BLINDAJE: Si "resultados" o "noticias" son texto (formato viejo), los convertimos en lista
                if "resultados" not in datos or isinstance(datos["resultados"], str):
                    print("⚠️ Detectado formato antiguo en vistos.json. Reparando automáticamente...")
                    datos["resultados"] = []
                if "noticias" not in datos or isinstance(datos["noticias"], str):
                    datos["noticias"] = []
                
                # Aseguramos que existan las otras claves por si acaso
                if "posiciones" not in datos: datos["posiciones"] = ""
                if "calendario" not in datos: datos["calendario"] = ""
                if "estadisticas" not in datos: datos["estadisticas"] = "" # <-- Agregado
                
                return datos
        except Exception as e:
            print(f"⚠️ Error al leer vistos.json ({e}). Creando uno nuevo...")
            
    # Si no existe o hubo error, devolvemos la estructura correcta desde cero
    return {
        "resultados": [],
        "posiciones": "",
        "calendario": "",
        "noticias": [],
        "estadisticas": "" # <-- Agregado
    }

def guardar_vistos(vistos):
    with open(VISTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(vistos, f, ensure_ascii=False, indent=2)

def enviar_a_telegram(mensaje):
    """Envía el mensaje al canal"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    datos = {
        "chat_id": CANAL,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    respuesta = requests.post(url, json=datos)
    return respuesta.status_code == 200

def main():
    print("🤖 Iniciando Bot Modular LVBP...")
    print("=" * 50)
    
    # 1. Cargar historial (ahora es 100% seguro)
    vistos = cargar_vistos()
    
    # ==========================================
    # 2. PROCESAR RESULTADOS
    # ==========================================
    print("📡 Extrayendo resultados...")
    data_resultados = resultados.obtener_ultimo_resultado()
    if data_resultados:
        if data_resultados["id"] not in vistos["resultados"]:
            print("✅ ¡Nuevo resultado detectado! Publicando...")
            if enviar_a_telegram(data_resultados["mensaje"]):
                vistos["resultados"].append(data_resultados["id"])
                print("📤 Enviado a Telegram con éxito.")
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ Este resultado ya fue publicado anteriormente.")
    else:
        print("⚠️ No se pudieron extraer resultados.")
    print("-" * 50)

    # ==========================================
    # 3. PROCESAR POSICIONES
    # ==========================================
    print("📡 Extrayendo posiciones...")
    data_posiciones = posiciones.obtener_tabla_posiciones()
    if data_posiciones:
        if data_posiciones["id"] != vistos.get("posiciones"):
            print("✅ ¡Posiciones actualizadas! Publicando...")
            if enviar_a_telegram(data_posiciones["mensaje"]):
                vistos["posiciones"] = data_posiciones["id"]
                print("📤 Enviado a Telegram con éxito.")
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ Las posiciones no han cambiado.")
    else:
        print("⚠️ No se pudieron extraer posiciones.")
    print("-" * 50)

    # ==========================================
    # 4. PROCESAR NOTICIAS
    # ==========================================
    print("📡 Extrayendo noticias...")
    data_noticias = noticias.obtener_ultima_noticia()
    if data_noticias:
        if data_noticias["id"] not in vistos["noticias"]:
            print("✅ ¡Nueva noticia detectada! Publicando...")
            if enviar_a_telegram(data_noticias["mensaje"]):
                vistos["noticias"].append(data_noticias["id"])
                print("📤 Enviado a Telegram con éxito.")
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ Esta noticia ya fue publicada anteriormente.")
    else:
        print("⚠️ No se pudieron extraer noticias.")
    print("-" * 50)

    # ==========================================
    # 5. PROCESAR CALENDARIO
    # ==========================================
    print("📡 Extrayendo calendario...")
    data_calendario = calendario.obtener_jornada_hoy()
    if data_calendario:
        if data_calendario["id"] != vistos.get("calendario"):
            print("✅ ¡Nueva jornada detectada! Publicando...")
            if enviar_a_telegram(data_calendario["mensaje"]):
                vistos["calendario"] = data_calendario["id"]
                print("📤 Enviado a Telegram con éxito.")
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ La jornada de hoy ya fue publicada.")
    else:
        print("⚠️ No se pudieron extraer datos del calendario.")
    print("-" * 50)

    # ==========================================
    # 6. PROCESAR ESTADÍSTICAS
    # ==========================================
    print("📡 Extrayendo estadísticas...")
    data_estadisticas = estadisticas.obtener_lideres_estadisticas()
    if data_estadisticas:
        if data_estadisticas["id"] != vistos.get("estadisticas"):
            print("✅ ¡Estadísticas actualizadas! Publicando...")
            if enviar_a_telegram(data_estadisticas["mensaje"]):
                vistos["estadisticas"] = data_estadisticas["id"]
                print("📤 Enviado a Telegram con éxito.")
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ Las estadísticas no han cambiado.")
    else:
        print("⚠️ No se pudieron extraer estadísticas.")
    print("=" * 50)
    
    # 7. Guardar historial actualizado
    print("💾 Guardando historial (vistos.json)...")
    guardar_vistos(vistos)
    print("✅ Bot completado exitosamente.")

if __name__ == '__main__':
    main()
