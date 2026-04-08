# -*- coding: utf-8 -*-
"""Geocodificar direcciones abril 2026 (Google Geocoding API)."""
import json
import urllib.parse
import urllib.request
import ssl
import time

API_KEY = "AIzaSyAEH7geT5dqaXiVNJ-L4EbcTHOIrlb05gs"

def geocode(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={API_KEY}&region=mx"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") == "OK" and data.get("results"):
        r = data["results"][0]
        loc = r["geometry"]["location"]
        return loc["lat"], loc["lng"], r.get("formatted_address", "")
    return None

if __name__ == "__main__":
    addrs = [
        ("Guasanga", "Calle Morelos 417, Col. Centro, Guadalajara, Jalisco, México"),
        ("GAMA", "Av. Américas 1254, Piso 10, Oficina 1, Country Club, Guadalajara, Jalisco, México"),
        ("Entre Charros", "Av. Ramón Michel 577, Rincón de la Agua Azul, Guadalajara, Jalisco, México"),
        ("La Esquina del Mar", "Mariano Bárcena 951, frente al Parque Alcalde, Guadalajara, Jalisco, México"),
        ("Academia", "Av. Hidalgo 107, Col. Centro, Guadalajara, Jalisco, México"),
        ("Calandrias", "Av. Miguel Hidalgo y Costilla 14, Zona Centro, Guadalajara, Jalisco, México"),
        ("Casa Carranza", "Calle Venustiano Carranza 242, Col. Centro, Guadalajara, Jalisco, México"),
    ]
    for name, a in addrs:
        g = geocode(a)
        time.sleep(0.25)
        print(f"=== {name} ===")
        if g:
            lat, lng, fmt = g
            print(f"  {lat:.7f}, {lng:.7f}")
            print(f"  {fmt}")
        else:
            print("  FAIL")
        print()
