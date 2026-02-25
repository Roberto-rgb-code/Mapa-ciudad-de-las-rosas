# -*- coding: utf-8 -*-
"""Geocode check completo: historicos + empresas. Verifica posiciones, duplicados y datos del tooltip."""
import json
import re
import urllib.request
import urllib.parse
import ssl
import time
from collections import defaultdict

API_KEY = "AIzaSyBNkRTHRBGK6YZqa34DmiZfEzc3bRynnd0"
THRESHOLD_M_OK = 150   # < 150m = OK
THRESHOLD_M_REVISAR = 400  # 150-400m = revisar, > 400m = mal ubicado
THRESHOLD_DUPLICADO_M = 20  # < 20m entre puntos = posible duplicado de coordenadas

def extract_places(html):
    """Extrae historicos y empresas del HTML."""
    places = []
    
    pattern = re.compile(
        r'nombre:\s*"((?:[^"\\]|\\.)*)"'
        r'.*?lat:\s*([\d.\-]+)'
        r'.*?lng:\s*([\d.\-]+)',
        re.DOTALL
    )
    dir_pattern = re.compile(r'direccion:\s*"((?:[^"\\]|\\.)*)"')
    
    hist_section = html.split("historicos:")[1].split("empresas:")[0]
    emp_section = html.split("empresas:")[1].split("],")[0]
    
    for section, tipo in [(hist_section, "historico"), (emp_section, "empresa")]:
        for m in pattern.finditer(section):
            nombre = m.group(1).replace('\\"', '"')
            lat = float(m.group(2))
            lng = float(m.group(3))
            block = section[m.start():m.end()+1500]  # bloque actual
            dm = dir_pattern.search(block)
            direccion = dm.group(1).replace('\\"', '"') if dm else ""
            places.append({
                "nombre": nombre,
                "lat": lat,
                "lng": lng,
                "direccion": direccion,
                "tipo": tipo,
                "idx": len(places),
            })
    
    return places


def dist_m(lat1, lng1, lat2, lng2):
    """Distancia aproximada en metros (haversine simplificado)."""
    import math
    R = 6371000  # radio Tierra en m
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def geocode(query, ctx):
    """Consulta Google Geocoding API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(query)}&key={API_KEY}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        if data["status"] == "OK" and data["results"]:
            r = data["results"][0]
            loc = r["geometry"]["location"]
            return {
                "lat": loc["lat"],
                "lng": loc["lng"],
                "formatted_address": r.get("formatted_address", ""),
                "place_id": r.get("place_id", ""),
            }
    except Exception as e:
        return {"error": str(e)}
    return None


def main():
    with open("mapa.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    places = extract_places(html)
    print(f"Extraídos: {len(places)} lugares ({sum(1 for p in places if p['tipo']=='historico')} históricos, {sum(1 for p in places if p['tipo']=='empresa')} empresas)\n")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 1. Detección de duplicados por coordenadas
    print("=" * 80)
    print("1. DUPLICADOS POR COORDENADAS (puntos muy cercanos)")
    print("=" * 80)
    duplicados = []
    for i, a in enumerate(places):
        for j, b in enumerate(places):
            if i >= j:
                continue
            d = dist_m(a["lat"], a["lng"], b["lat"], b["lng"])
            if d < THRESHOLD_DUPLICADO_M:
                duplicados.append((i, j, d, a, b))
    
    if duplicados:
        for i, j, d, a, b in duplicados:
            print(f"  DUPLICADO: {d:.0f}m entre:")
            print(f"    [{a['idx']}] {a['nombre']} (lat: {a['lat']}, lng: {a['lng']})")
            print(f"    [{b['idx']}] {b['nombre']} (lat: {b['lat']}, lng: {b['lng']})")
            if a["direccion"] or b["direccion"]:
                print(f"    Dir A: {a['direccion'][:60]}...")
                print(f"    Dir B: {b['direccion'][:60]}...")
            print()
    else:
        print("  Ninguno detectado.\n")
    
    # 2. Duplicados por nombre (mismo nombre, diferentes ubicaciones - puede ser sucursales)
    print("=" * 80)
    print("2. MISMOS NOMBRES CON DIFERENTES UBICACIONES (sucursales / duplicado?)")
    print("=" * 80)
    by_nombre = defaultdict(list)
    for p in places:
        # Normalizar nombre para comparar (quitar prefijos RESTAURANT, HOTEL, etc.)
        n = p["nombre"].strip().upper()
        by_nombre[n].append(p)
    
    for nombre, pts in by_nombre.items():
        if len(pts) > 1:
            print(f"  {nombre}: {len(pts)} ubicaciones")
            for p in pts:
                print(f"    [{p['idx']}] {p['direccion'][:70] if p['direccion'] else '(sin direccion)'} ({p['lat']:.6f}, {p['lng']:.6f})")
            print()
    
    # 3. Geocoding: verificar coordenadas contra Google
    print("=" * 80)
    print("3. VERIFICACIÓN GEOCODING (Google API)")
    print("=" * 80)
    
    results = []
    for i, p in enumerate(places):
        query = p["direccion"] if p["direccion"] and "Contrataciones" not in p["direccion"] else f"{p['nombre']}, Guadalajara, Jalisco, Mexico"
        g = geocode(query, ctx)
        time.sleep(0.15)  # rate limit
        
        if g and "error" not in g:
            d = dist_m(p["lat"], p["lng"], g["lat"], g["lng"])
            if d < THRESHOLD_M_OK:
                status = "OK"
            elif d < THRESHOLD_M_REVISAR:
                status = "REVISAR"
            else:
                status = "MAL_UBICADO"
            results.append({
                "idx": p["idx"],
                "nombre": p["nombre"],
                "tipo": p["tipo"],
                "actual": [p["lat"], p["lng"]],
                "google": [g["lat"], g["lng"]],
                "dist_m": round(d),
                "status": status,
                "direccion_tooltip": p["direccion"],
                "direccion_google": g["formatted_address"],
            })
            symb = "OK" if status == "OK" else ("!!" if status == "REVISAR" else "XX")
            print(f"  {symb} {status:12} | {d:6.0f}m | [{p['idx']:2}] {p['nombre'][:45]}")
            if status != "OK":
                print(f"         | actual:  {p['lat']}, {p['lng']}")
                print(f"         | google:  {g['lat']}, {g['lng']}")
                print(f"         | tooltip: {p['direccion'][:70] if p['direccion'] else '(vacio)'}...")
                print(f"         | google:  {g['formatted_address'][:70]}...")
        else:
            err = g.get("error", "NO_FOUND") if g else "NO_FOUND"
            print(f"  ? NO_FOUND/ERROR |        | [{p['idx']:2}] {p['nombre'][:45]} -> {err}")
            results.append({
                "idx": p["idx"],
                "nombre": p["nombre"],
                "tipo": p["tipo"],
                "status": "NO_FOUND",
                "error": str(err),
            })
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    ok = sum(1 for r in results if r.get("status") == "OK")
    rev = sum(1 for r in results if r.get("status") == "REVISAR")
    mal = sum(1 for r in results if r.get("status") == "MAL_UBICADO")
    nf = sum(1 for r in results if r.get("status") in ("NO_FOUND", "ERROR"))
    print(f"  OK:           {ok}")
    print(f"  Revisar:      {rev}")
    print(f"  Mal ubicado:  {mal}")
    print(f"  No encontrado:{nf}")
    print(f"  Duplicados coord: {len(duplicados)} pares")
    
    with open("geocode_reporte.json", "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "duplicados_coordenadas": [
                {"idx1": a["idx"], "idx2": b["idx"], "dist_m": round(d), "nombre1": a["nombre"], "nombre2": b["nombre"]}
                for i, j, d, a, b in duplicados
            ],
            "resumen": {"ok": ok, "revisar": rev, "mal_ubicado": mal, "no_encontrado": nf},
        }, f, ensure_ascii=False, indent=2)
    
    print("\nReporte guardado en geocode_reporte.json")


if __name__ == "__main__":
    main()
