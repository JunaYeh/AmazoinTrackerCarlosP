import os
import requests
from bs4 import BeautifulSoup

# Variables de entorno que configuraremos en GitHub
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://www.amazon.com.mx/dp/B0HFM9NTC1"

# Simular que somos un navegador real es vital para Amazon
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def enviar_alerta(mensaje):
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url_api, json=payload)

def monitorear_amazon():
    try:
        respuesta = requests.get(URL, headers=HEADERS, timeout=15)
        
        # Amazon a veces devuelve 503 si detecta bots
        if respuesta.status_code != 200:
            print(f"Error al acceder. Código: {respuesta.status_code}")
            return

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Buscamos el botón de compra o de agregar al carrito
        # Esto nos indica que el producto está disponible para comprar
        boton_comprar = soup.find(id="add-to-cart-button")
        
        if boton_comprar:
            enviar_alerta(f"🚨 ¡CAMBIO DETECTADO! 🚨\nEl producto parece estar disponible o hubo un cambio importante.\nRevisa aquí: {URL}")
            print("Alerta enviada.")
        else:
            print("Sin cambios relevantes o producto no disponible.")
            
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__ == "__main__":
    monitorear_amazon()