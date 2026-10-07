import os
import time
import random
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://www.amazon.com.mx/dp/B0HFM9NTC1"

# Lista de navegadores para ir rotando y disimular ante Amazon
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
]

def enviar_alerta(mensaje):
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url_api, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def revisar_pagina():
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com.mx/",
        "Connection": "keep-alive"
    }
    
    try:
        respuesta = requests.get(URL, headers=headers, timeout=15)
        
        if respuesta.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] Bloqueo o error de Amazon. Código: {respuesta.status_code}")
            return False

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Verifica si Amazon nos mandó un CAPTCHA en lugar de la página
        if soup.find("form", {"action": "/errors/validateCaptcha"}):
            print(f"[{time.strftime('%H:%M:%S')}] Amazon detectó el bot y pidió CAPTCHA.")
            return False

        # Busca los botones de compra habituales
        boton_carrito = soup.find(id="add-to-cart-button")
        boton_comprar_ya = soup.find(id="buy-now-button")
        
        if boton_carrito or boton_comprar_ya:
            enviar_alerta(f"🚨 ¡DISPONIBLE EN AMAZON! 🚨\nYa aparece el botón de compra.\nCorre al link: {URL}")
            print(f"[{time.strftime('%H:%M:%S')}] ¡Cambio detectado! Alerta enviada.")
            return True
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Sin stock / Sin cambios.")
            return False
            
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error de conexión: {e}")
        return False

if __name__ == "__main__":
    # Ejecuta 28 revisiones separadas por 2 minutos (cubre ~56 minutos en total)
    ITERACIONES = 28
    INTERVALO_SEGUNDOS = 120 # 2 minutos

    print("Iniciando ciclo de monitoreo cada 2 minutos...")
    for i in range(ITERACIONES):
        print(f"--- Revisión {i+1} de {ITERACIONES} ---")
        encontrado = revisar_pagina()
        
        # Si ya encontró el producto, espera 10 minutos antes de volver a avisar para no saturar tu Telegram
        if encontrado:
            time.sleep(600)
        elif i < ITERACIONES - 1:
            time.sleep(INTERVALO_SEGUNDOS)
