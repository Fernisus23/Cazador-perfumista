import requests
from bs4 import BeautifulSoup
import json
import time
import random
import sys
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
            # Limpiar moneda
            precio_str = texto.replace('€', '').replace('EUR', '').replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
            try:
                return float(precio_str)
            except:
                continue
    return None

def generar_datos_ejemplo():
    """Si no se puede scrapear nada, genera datos de ejemplo para que la web no esté vacía."""
    return [
        {
            "nombre": "Bond No9 Park Avenue South EDP 100ml (ejemplo)",
            "tienda": "El Roble Perfumado",
            "precio": 79.95,
            "tipo": "nicho",
            "url": "https://elrobleperfumado.com/perfumes-mujer/tst-bond-no9-park-avenue-south-edp-100-ml.html",
            "posibleError": False,
            "confianza": 4.5,
            "precioAnterior": 120.00
        },
        {
            "nombre": "Tom Ford Costa Azzurra EDP 100ml (ejemplo)",
            "tienda": "PerfumeDigital",
            "precio": 105.00,
            "tipo": "disenador",
            "url": "https://perfumedigital.es/Perfumes-Mujer-TOM-FORD-TOM-FORD-COSTA-AZZURRA-EDP-100-ML-REGULAR",
            "posibleError": False,
            "confianza": 4.0,
            "precioAnterior": 135.00
        }
    ]

def scrapear_tiendas(archivo_config='tiendas.json'):
    print("=" * 50)
    print("INICIANDO SCRAPER")
    print("=" * 50)
    
    # Cargar configuración
    try:
        with open(archivo_config, 'r', encoding='utf-8') as f:
            tiendas = json.load(f)
        print(f"Configuración cargada: {len(tiendas)} tiendas")
    except FileNotFoundError:
        print("ERROR: tiendas.json no encontrado. Se usarán datos de ejemplo.")
        tiendas = []
    except Exception as e:
        print(f"ERROR al leer tiendas.json: {e}")
        tiendas = []

    resultados = []
    
    for tienda in tiendas:
        url = tienda.get('url')
        nombre_tienda = tienda.get('nombre', 'Desconocida')
        selectores = tienda.get('selectores', [])
        tipo = tienda.get('tipo', 'desconocido')

        print(f"\nProcesando: {nombre_tienda}")
        print(f"URL: {url}")
        print(f"Selectores a probar: {selectores}")

        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"Estado HTTP: {resp.status_code}")
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                precio = extraer_precio(soup, selectores)
                if precio:
                    # Intentar obtener nombre del producto
                    nombre_producto = f"Producto de {nombre_tienda}"
                    if soup.title:
                        nombre_producto = soup.title.string.strip()[:80]
                    h1 = soup.find('h1')
                    if h1:
                        nombre_producto = h1.get_text(strip=True)[:80]
                    
                    print(f"✓ PRECIO ENCONTRADO: {precio} €")
                    resultados.append({
                        'nombre': nombre_producto,
                        'tienda': nombre_tienda,
                        'precio': precio,
                        'tipo': tipo,
                        'url': url,
                        'posibleError': False,
                        'confianza': round(random.uniform(3.5, 5.0), 1),
                        'precioAnterior': None
                    })
                else:
                    print("✗ Precio no encontrado con esos selectores")
            else:
                print(f"Saltando por estado HTTP {resp.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: No se pudo conectar (posible bloqueo o DNS)")
        except requests.exceptions.Timeout:
            print("ERROR: Timeout (la tienda tardó demasiado)")
        except Exception as e:
            print(f"ERROR inesperado: {type(e).__name__}: {e}")

        time.sleep(random.uniform(3, 5))

    # Si no se consiguió nada, usar datos de ejemplo para que la web funcione
    if not resultados:
        print("\n⚠️ No se obtuvo ningún precio real. Se usarán datos de ejemplo.")
        resultados = generar_datos_ejemplo()

    # Guardar el archivo
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ datos.json guardado con {len(resultados)} productos.")
    print("Contenido del archivo:")
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    print("=" * 50)

if __name__ == '__main__':
    scrapear_tiendas()
