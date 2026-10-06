import requests
import os

# Datos del bot
TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

# Función para enviar mensaje al canal
def enviar_mensaje(mensaje):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    datos = {
        'chat_id': CHANNEL,
        'text': mensaje,
        'parse_mode': 'HTML'
    }
    respuesta = requests.post(url, data=datos)
    return respuesta.json()

# Mensaje de prueba
mensaje = """
⚾ <b>Resultados LVBP - Prueba del Bot</b>

🏟️ Este es un mensaje de prueba del bot automático.

✅ El bot está funcionando correctamente.
📅 Pronto publicará los resultados reales de la LVBP.

🔗 Canal: @LVBPAlDia
💬 Grupo: @lvbpaldia_comunidad
"""

# Enviar el mensaje
resultado = enviar_mensaje(mensaje)

if resultado.get('ok'):
    print("✅ Mensaje enviado correctamente al canal")
else:
    print("❌ Error al enviar el mensaje:", resultado)
