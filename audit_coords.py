import re
import os
import json
import urllib.parse
import urllib.request

# --- Configuración ---
FILE = "mapa.html"
GDL_CENTER = (20.6767, -103.347)
# Límites aproximados del Centro Histórico ampliado (donde deben estar la mayoría)
BOUNDS = {
    "lat_min": 20.60, "lat_max": 20.75,
    "lng_min": -103.45, "lng_max": -103.30
}

def extraer_lugares(content):
    # Simplificado: extraer bloques { ... }
    matches = re.finditer(r'\{[^{}]*?nombre:\s*["\'](.*?)["\'].*?\}', content, re.DOTALL)
    lugares = []
    for m in matches:
        obj_str = m.group(0)
        nombre = m.group(1)
        lat_m = re.search(r'lat:\s*([\d.-]+)', obj_str)
        lng_m = re.search(r'lng:\s*([\d.-]+)', obj_str)
        dir_m = re.search(r'direccion:\s*["\'](.*?)["\']', obj_str)
        if lat_m and lng_m:
            lugares.append({
                "nombre": nombre,
                "lat": float(lat_m.group(1)),
                "lng": float(lng_m.group(1)),
                "direccion": dir_m.group(1) if dir_m else ""
            })
    return lugares

def main():
    if not os.path.exists(FILE):
        print(f"Error: {FILE} no existe.")
        return

    with open(FILE, "r", encoding="utf-8") as f:
        content = f.read()

    puntos = extraer_lugares(content)
    print(f"Auditando {len(puntos)} puntos en {FILE}...")
    
    problemas = []
    for p in puntos:
        fuera = False
        lat = float(p["lat"])
        lng = float(p["lng"])
        if not (float(BOUNDS["lat_min"]) <= lat <= float(BOUNDS["lat_max"])): fuera = True
        if not (float(BOUNDS["lng_min"]) <= lng <= float(BOUNDS["lng_max"])): fuera = True
        
        if fuera:
            problemas.append(f"FUERA DE GDL: {p['nombre']} ({lat}, {lng}) - Dir: {p['direccion']}")
        
        # Especial: Calandrias
        if "CALANDRIAS" in str(p["nombre"]) and "Santa Mónica" in str(p["direccion"]):
            # Debería estar cerca de -103.3485
            if abs(lng - (-103.34853)) > 0.001:
                problemas.append(f"DESALINEADO: {p['nombre']} está en {lat}, {lng} pero su dir dice Santa Mónica.")

    if problemas:
        print("\nSe encontraron problemas:")
        for prob in problemas:
            print(f"  - {prob}")
    else:
        print("\nNo se detectaron problemas de ubicación obvios.")

if __name__ == "__main__":
    main()
