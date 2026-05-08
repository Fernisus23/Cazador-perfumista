import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

def extraer_precio(soup, selectores):
    for selector in selectores:
        elem = soup.select_one(selector)
        if elem:
            texto = elem.get_text(strip=True)
            # Limpiar símbolos de moneda y espacios
            precio_str = texto.replace('€', '').replace('EUR', '').replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
            try:
                return float(precio_str)
            except:
                continue
    return None

def scrapear_tiendas(archivo_config='tiendas.json'):
    with open(archivo_config, 'r', encoding='utf-8') as f:
        tiendas = json.load(f)

    resultados = []
    for tienda in tiendas:
        url = tienda['url']
        nombre_tienda = tienda['nombre']
        selectores = tienda['selectores']
        tipo = tienda.get('tipo', 'desconocido')

        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"Error {resp.status_code} en {nombre_tienda}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            precio = extraer_precio(soup, selectores)
            if precio:
                # Intentar extraer nombre del producto desde el título o un h1
                nombre_producto = "Desconocido"
                if soup.title:
                    nombre_producto = soup.title.string.strip()
                h1 = soup.find('h1')
                if h1:
                    nombre_producto = h1.get_text(strip=True)

                resultados.append({
                    'nombre': nombre_producto[:80],
                    'tienda': nombre_tienda,
                    'precio': precio,
                    'tipo': tipo,
                    'url': url,
                    'posibleError': False,
                    'confianza': 4.0,
                    'precioAnterior': None
                })
                print(f"✓ {nombre_tienda}: {precio}€")
            else:
                print(f"✗ {nombre_tienda}: precio no encontrado")
        except Exception as e:
            print(f"Error en {nombre_tienda}: {e}")

        time.sleep(random.uniform(2, 4))  # Pausa para no saturar

    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"Guardados {len(resultados)} resultados.")

if __name__ == '__main__':
    scrapear_tiendas()
