# -*- coding: utf-8 -*-
"""Verifica coordenadas de puntos específicos usando Google Geocoding API.
   Uso: python geocode_verificar_puntos.py
   Verifica: item 28 (Hidalgo y Federalismo), y otros puntos del mapa."""
import json
import urllib.request
import urllib.parse
import ssl
import time

API_KEY = "AIzaSyAEH7geT5dqaXiVNJ-L4EbcTHOIrlb05gs"

def geocode(query):
    """Consulta Google Geocoding API. Retorna (lat, lng, formatted_address) o None."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(query)}&key={API_KEY}"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        if data["status"] == "OK" and data["results"]:
            r = data["results"][0]
            loc = r["geometry"]["location"]
            return (loc["lat"], loc["lng"], r.get("formatted_address", ""))
    except Exception as e:
        print(f"  Error: {e}")
    return None

def dist_m(lat1, lng1, lat2, lng2):
    """Distancia aproximada en metros (Haversine)."""
    import math
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def main():
    # Puntos a verificar según lista de correcciones
    puntos = [
        # (nombre, direccion_actual, lat_actual, lng_actual, nota)
        ("28 - ACADEMIA Nuevo Jalisco (Hidalgo y Federalismo)", "Av. Hidalgo 107, Centro, Guadalajara, Jalisco, México", 20.6773869, -103.3431894, "En mapa debe estar en Hidalgo y Federalismo"),
        ("28 - Intersección Hidalgo y Federalismo", "Av. Hidalgo y Calz. Federalismo, Guadalajara, Jalisco, México", None, None, "Coordenadas de la intersección"),
        ("32 - Verificar ubicación", None, None, None, "Item 32: buscar de cerca (verificar en mapa)"),
    ]

    print("=" * 70)
    print("Verificación de coordenadas - Google Geocoding API")
    print("=" * 70)

    for nombre, direccion, lat, lng, nota in puntos:
        print(f"\n{nombre}")
        print(f"  Nota: {nota}")
        if direccion:
            g = geocode(direccion)
            time.sleep(0.2)
            if g:
                glat, glng, addr = g
                print(f"  Dirección: {direccion}")
                print(f"  Google:    {addr}")
                print(f"  Coord:     {glat:.6f}, {glng:.6f}")
                if lat is not None and lng is not None:
                    d = dist_m(lat, lng, glat, glng)
                    status = "OK" if d < 150 else ("REVISAR" if d < 400 else "MAL_UBICADO")
                    print(f"  Actual:    {lat:.6f}, {lng:.6f}")
                    print(f"  Distancia: {d:.0f}m -> {status}")
        else:
            print("  (Sin dirección para geocodificar)")

    print("\n" + "=" * 70)
    print("Para actualizar coordenadas en index.html y mapa.html, edita manualmente")
    print("o usa el resultado de arriba para corregir lat/lng en lugares.empresas.")
    print("=" * 70)

if __name__ == "__main__":
    main()
