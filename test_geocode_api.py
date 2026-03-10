# -*- coding: utf-8 -*-
"""Test rápido: verifica que la API de Google Geocoding funciona."""
import json
import urllib.request
import urllib.parse
import ssl

API_KEY = "AIzaSyBNkRTHRBGK6YZqa34DmiZfEzc3bRynnd0"

def test_geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urllib.parse.urlencode({
        "address": address,
        "key": API_KEY,
        "region": "mx",
        "components": "administrative_area:Jalisco|country:MX",
    })
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
            return {"lat": loc["lat"], "lng": loc["lng"], "addr": r.get("formatted_address", "")}
        return {"error": data.get("status", "NO_RESULTS")}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    tests = [
        "Catedral de Guadalajara, Av. Alcalde, Guadalajara",
        "Glorieta Minerva, Av. López Mateos y Vallarta, Guadalajara",
        "Los Arcos de Guadalajara, Av. Vallarta 2585, Guadalajara",
    ]
    print("=== TEST API GEOCODING ===\n")
    for q in tests:
        r = test_geocode(q)
        if "error" in r:
            print("FALLO:", q[:50], "->", r["error"])
        else:
            print("OK   ", q[:50])
            print("     ", r["lat"], r["lng"])
            print("     ", r["addr"][:70], "...")
        print()
