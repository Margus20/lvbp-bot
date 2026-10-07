import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL = '@LVBPAlDia'

def main():
    print("Iniciando...")
    total = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.tiburonesbbc.com/noticias', wait_until='networkidle', timeout=30000)
        time.sleep(5)
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    if len(articles) == 0:
        articles = soup.find_all('div')
    for art in articles[:3]:
        img_tag = art.find('img')
        img_url = None
        if img_tag:
            img_url = img_tag.get('src')
            if img_url and not img_url.startswith('http'):
                img_url = 'https://www.tiburonesbbc.com' + img_url
        titulo_tag = art.find(['h1', 'h2', 'h3'])
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
        p_tag = art.find('p')
        resumen = p_tag.get_text(strip=True)[:200] if p_tag else ""
        if titulo and len(titulo) > 10:
            texto = "🦈 TIBURONES\n\n" + titulo + "\n\n" + resumen
            url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
            datos = {'chat_id': CHANNEL, 'text': texto, 'parse_mode': 'HTML'}
            requests.post(url, data=datos, timeout=15)
            total += 1
    calendario = "🦈 CALENDARIO TIBURONES - OCTUBRE 2026\n\nSEMANA 1:\n13 Mar: vs MAGALLANES\n15 Jue: vs ANZOATEGUI\n16 Vie: vs ANZOATEGUI\n17 Sab: vs ARAGUA\n18 Dom: vs ARAGUA\n\nSEMANA 2:\n20 Mar: vs CARACAS\n21 Mie: vs MAGALLANES\n22 Jue: vs MARGARITA\n23 Vie: vs MARGARITA\n24 Sab: vs ANZOATEGUI\n25 Dom: vs ANZOATEGUI\n\nSEMANA 3:\n27 Mar: vs MAGALLANES\n28 Mie: vs CARACAS\n29 Jue: vs LARA\n30 Vie: vs ZULIA\n31 Sab: vs LARA\n\nRojo = Local | Blanco = Visita\n¡Que comience la temporada!"
    url2 = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    datos2 = {'chat_id': CHANNEL, 'text': calendario}
    requests.post(url2, data=datos2, timeout=15)
    total += 1
    print("Total: " + str(total))

if __name__ == '__main__':
    main()
