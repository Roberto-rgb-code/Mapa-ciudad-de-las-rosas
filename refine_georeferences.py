#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refina y sincroniza los puntos de mapa.html e index.html con la API de Google Maps.
Usa Places API para alta precisión (nombre + dirección) y Geocoding como respaldo.
"""
import re
import os
import json
import time
import urllib.parse
import urllib.request

# --- Configuración ---
FILES_TO_UPDATE = ["mapa.html", "index.html"]
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "AIzaSyAEH7geT5dqaXiVNJ-L4EbcTHOIrlb05gs")
SUFIJO = ", Guadalajara, Jalisco, México"
DELAY_SEC = 0.2
GDL_CENTER = "20.6767,-103.347"
GDL_BIAS_RADIUS = 35000

def extraer_objetos_con_braces(content, inicio_marker):
    idx = content.find(inicio_marker)
    if idx == -1: return []
    idx = content.find("[", idx) + 1
    resultados = []
    n = len(content)
    while idx < n:
        while idx < n and content[idx] in " \t\n\r,":
            idx += 1
        if idx >= n or content[idx] == "]": break
        if content[idx] != "{":
            idx += 1
            continue
        start = idx
        depth = 1
        idx += 1
        while idx < n and depth > 0:
            if content[idx] == '"':
                idx += 1
                while idx < n and content[idx] != '"':
                    if content[idx] == "\\": idx += 1
                    idx += 1
                if idx < n: idx += 1
                continue
            if content[idx] == "'":
                idx += 1
                while idx < n and content[idx] != "'":
                    if content[idx] == "\\": idx += 1
                    idx += 1
                if idx < n: idx += 1
                continue
            if content[idx] == "{": depth += 1
            elif content[idx] == "}": depth -= 1
            idx += 1
        end = idx - 1
        obj_str = content[start : end + 1]
        resultados.append((obj_str, start, end))
    return resultados

def extraer_campos(obj_str):
    def get_quoted(pat):
        m = re.search(pat, obj_str, re.DOTALL)
        if m: return m.group(1).replace('\\"', '"').replace("\\'", "'").strip()
        return None
    def get_num(pat):
        m = re.search(pat, obj_str)
        if m:
            try: return float(m.group(1))
            except ValueError: pass
        return None
    nombre = get_quoted(r'nombre:\s*["\']((?:[^"\'\\]|\\.)*)["\']')
    direccion = get_quoted(r'direccion:\s*["\']((?:[^"\'\\]|\\.)*)["\']')
    lat = get_num(r'lat:\s*([\d.-]+)')
    lng = get_num(r'lng:\s*([\d.-]+)')
    return nombre, direccion, lat, lng

def find_place_google(nombre, direccion, api_key):
    query = (nombre + ", " + direccion).strip()
    if not any(x in query for x in ["Guadalajara", "Jalisco", "México"]):
        query += SUFIJO
    params = {
        "input": query[:200],
        "inputtype": "textquery",
        "fields": "geometry,formatted_address,name",
        "key": api_key,
        "language": "es",
        "locationbias": "circle:%d@%s" % (GDL_BIAS_RADIUS, GDL_CENTER),
    }
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e: return None, None, None, None, str(e)
    if data.get("status") != "OK": return None, None, None, None, data.get("status", "ERROR")
    candidates = data.get("candidates") or []
    if not candidates: return None, None, None, None, "ZERO_RESULTS"
    c = candidates[0]
    loc = c.get("geometry", {}).get("location", {})
    lat, lng = loc.get("lat"), loc.get("lng")
    if lat is None or lng is None: return None, None, None, None, "NO_GEOMETRY"
    return lat, lng, c.get("formatted_address", ""), c.get("name", ""), None

def geocode_address(address, api_key):
    full = address.strip()
    if not any(x in full for x in ["Guadalajara", "Jalisco", "México"]):
        full += SUFIJO
    bounds = "20.55,-103.42|20.75,-103.28"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + urllib.parse.quote(full) + "&bounds=" + bounds + "&region=mx&key=" + api_key
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e: return None, None, None, str(e)
    if data.get("status") != "OK" or not data.get("results"): return None, None, None, data.get("status", "ZERO_RESULTS")
    r = data["results"][0]
    loc = r["geometry"]["location"]
    return loc["lat"], loc["lng"], r.get("formatted_address", ""), None

def process_file(filepath):
    print(f"Procesando {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    markers_data = []
    for tipo, marker_start in [("historicos", "historicos: ["), ("empresas", "empresas: [")]:
        objs = extraer_objetos_con_braces(content, marker_start)
        for obj_str, start, end in objs:
            nombre, direccion, lat, lng = extraer_campos(obj_str)
            if nombre or direccion:
                markers_data.append({
                    "tipo": tipo, "nombre": nombre or "", "direccion": direccion or "",
                    "lat_old": lat, "lng_old": lng, "start": start, "end": end, "obj_str": obj_str
                })

    updates = []
    for i, m in enumerate(markers_data):
        if not m["direccion"] or m["direccion"].strip().startswith("Contrataciones"):
            continue
        print(f"  [{i+1}/{len(markers_data)}] {m['nombre'][:40]}...", end="\r")
        time.sleep(DELAY_SEC)
        
        lat_n, lng_n, addr, p_name, err = find_place_google(m["nombre"], m["direccion"], API_KEY)
        if lat_n is None:
            lat_n, lng_n, addr, err = geocode_address(m["direccion"], API_KEY)
        
        if lat_n is not None:
            # Reemplazo de coordenadas en el bloque original
            bloque = m["obj_str"]
            pat = r'lat:\s*[\d.-]+,\s*lng:\s*[\d.-]+'
            # Mantener formato de indentación aproximado
            new_coords = f'lat: {lat_n},\n                    lng: {lng_n}'
            new_bloque = re.sub(pat, new_coords, bloque, count=1)
            if new_bloque != bloque:
                updates.append((m["start"], m["end"] + 1, new_bloque))

    # Aplicar de atrás hacia adelante
    new_content = content
    for start, end, new_bloque in sorted(updates, key=lambda x: -x[0]):
        new_content = new_content[:start] + new_bloque + new_content[end:]
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"\n{filepath} actualizado: {len(updates)} cambios aplicados.")

def main():
    for f in FILES_TO_UPDATE:
        if os.path.exists(f):
            process_file(f)
        else:
            print(f"Archivo {f} no encontrado.")
    print("Sincronización completada.")

if __name__ == "__main__":
    main()
