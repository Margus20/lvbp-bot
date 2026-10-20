# config.py
import os

# Configuración de Telegram
TOKEN = os.environ.get('BOT_TOKEN', 'TU_TOKEN_AQUI') # Pon tu token aquí si no usas variables de entorno
CANAL = '@LVBPalDia'
TU_PAGINA = 'https://margus20.github.io/lvbp-stats/'

# URLs directas a los archivos JS de tu repositorio (Raw)
REPO_BASE = 'https://raw.githubusercontent.com/Margus20/lvbp-stats/main/js/datos/'

URLS_DATOS = {
    'posiciones': f"{REPO_BASE}posiciones.js",
    'resultados': f"{REPO_BASE}resultados.js",
    'calendario': f"{REPO_BASE}calendario.js",
    'noticias': f"{REPO_BASE}noticias.js",
    'lideres': f"{REPO_BASE}lideres.js"
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
