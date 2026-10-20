# main.py
import os
import json
import requests
from config import TOKEN, CANAL
from extractores import resultados

VISTOS_FILE = 'vistos.json'

def cargar_vistos():
    """Carga el historial o lo repara automáticamente si tiene el formato viejo."""
    if os.path.exists(VISTOS_FILE):
        try:
            with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
                # BLINDAJE: Si "resultados" es un texto (formato viejo) o no existe, lo convertimos en lista
                if "resultados" not in datos or isinstance(datos["resultados"], str):
                    print("⚠️ Detectado formato antiguo en vistos.json. Reparando automáticamente...")
                    datos["resultados"] = []
                
                # Aseguramos que existan las otras claves por si acaso
                if "posiciones" not in datos: datos["posiciones"] = ""
                if "calendario" not in datos: datos["calendario"] = ""
                if "noticias" not in datos: datos["noticias"] = []
                
                return datos
        except Exception as e:
            print(f"⚠️ Error al leer vistos.json ({e}). Creando uno nuevo...")
            
    # Si no existe o hubo error, devolvemos la estructura correcta desde cero
    return {
        "resultados": [],
        "posiciones": "",
        "calendario": "",
        "noticias": []
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
    
    # 1. Cargar historial (ahora es 100% seguro)
    vistos = cargar_vistos()
    
    # 2. Pedirle al módulo de resultados que extraiga la info
    print("📡 Extrayendo resultados...")
    data_resultados = resultados.obtener_ultimo_resultado()
    
    if data_resultados:
        id_unico = data_resultados["id"]
        
        # 3. Verificar si ya lo publicamos
        if id_unico not in vistos["resultados"]:
            print("✅ ¡Nuevo resultado detectado! Publicando...")
            
            if enviar_a_telegram(data_resultados["mensaje"]):
                print("📤 Enviado a Telegram con éxito.")
                # Guardar en historial para no repetir
                vistos["resultados"].append(id_unico)
                guardar_vistos(vistos)
            else:
                print("❌ Falló el envío a Telegram.")
        else:
            print("⏭️ Este resultado ya fue publicado anteriormente.")
    else:
        print("⚠️ No se pudieron extraer resultados.")

if __name__ == '__main__':
    main()
