# main.py
import os
import json
import requests
from config import TOKEN, CANAL
from extractores import resultados

VISTOS_FILE = 'vistos.json'

def cargar_vistos():
    if os.path.exists(VISTOS_FILE):
        with open(VISTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"resultados": []}

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
    
    # 1. Cargar historial
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
