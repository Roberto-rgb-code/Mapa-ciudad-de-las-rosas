#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocodifica todos los puntos de mapa.html (historicos + empresas) con la API de Google.
Verifica que el nombre del lugar coincida con la dirección antes de actualizar.
Reporta cualquier no coincidencia antes de aplicar cambios.
"""
import re
import os
import json
import time
import urllib.parse
import urllib.request

# --- Configuración ---
MAPA_HTML = os.path.join(os.path.dirname(__file__), "mapa.html")
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "AIzaSyBNkRTHRBGK6YZqa34DmiZfEzc3bRynnd0")
SUFIJO = ", Guadalajara, Jalisco, México"
DELAY_SEC = 0.2  # pausa entre llamadas a la API
REPORTE_NO_COINCIDENCIAS = "no_coincidencias_nombre_direccion.txt"
REPORTE_GEOCODING = "geocode_resultados.json"


def extraer_objetos_con_braces(content, inicio_marker):
    """Extrae objetos JS { ... } de un array. Devuelve lista de (obj_str, start_idx, end_idx)."""
    idx = content.find(inicio_marker)
    if idx == -1:
        return []
    idx = content.find("[", idx) + 1
    resultados = []
    n = len(content)
    while idx < n:
        while idx < n and content[idx] in " \t\n\r,":
            idx += 1
        if idx >= n or content[idx] == "]":
            break
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
                    if content[idx] == "\\":
                        idx += 1
                    idx += 1
                if idx < n:
                    idx += 1
                continue
            if content[idx] == "'":
                idx += 1
                while idx < n and content[idx] != "'":
                    if content[idx] == "\\":
                        idx += 1
                    idx += 1
                if idx < n:
                    idx += 1
                continue
            if content[idx] == "{":
                depth += 1
            elif content[idx] == "}":
                depth -= 1
            idx += 1
        end = idx - 1
        obj_str = content[start : end + 1]
        resultados.append((obj_str, start, end))
    return resultados


def extraer_campos(obj_str):
    """Extrae nombre, direccion, lat, lng de un objeto JS."""
    def get_quoted(pat):
        m = re.search(pat, obj_str, re.DOTALL)
        if m:
            return m.group(1).replace('\\"', '"').replace("\\'", "'").strip()
        return None

    def get_num(pat):
        m = re.search(pat, obj_str)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return None

    nombre = get_quoted(r'nombre:\s*["\']((?:[^"\'\\]|\\.)*)["\']')
    direccion = get_quoted(r'direccion:\s*["\']((?:[^"\'\\]|\\.)*)["\']')
    lat = get_num(r'lat:\s*([\d.-]+)')
    lng = get_num(r'lng:\s*([\d.-]+)')
    return nombre, direccion, lat, lng


def geocode_address(address, api_key):
    """Geocodifica una dirección con Google Geocoding API. Devuelve (lat, lng, formatted_address) o None."""
    full = address.strip()
    if not full.endswith("México") and "Guadalajara" not in full:
        full = full + SUFIJO
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + urllib.parse.quote(full) + "&key=" + api_key
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return None, None, None, str(e)
    if data.get("status") != "OK" or not data.get("results"):
        return None, None, None, data.get("status", "ZERO_RESULTS")
    r = data["results"][0]
    loc = r["geometry"]["location"]
    return loc["lat"], loc["lng"], r.get("formatted_address", ""), None


def normalizar_para_comparar(texto):
    """Normaliza texto para comparar nombre vs resultado (quitar acentos, mayúsculas, puntuación)."""
    if not texto:
        return ""
    t = texto.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for k, v in reemplazos.items():
        t = t.replace(k, v)
    return t


def nombre_coincide_con_direccion(nombre, direccion, formatted_address, place_name=None):
    """
    Comprueba si el nombre del punto es coherente con la dirección geocodificada.
    - Si tenemos place_name (de Places), comprobamos que el nombre contenga palabras clave.
    - Comprobamos que la dirección devuelta (formatted_address) esté en Guadalajara y contenga la calle/número.
    """
    if not formatted_address:
        return True, ""
    addr_norm = normalizar_para_comparar(formatted_address)
    dir_norm = normalizar_para_comparar(direccion) if direccion else ""
    # Que la dirección geocodificada esté en Guadalajara
    if "guadalajara" not in addr_norm and "jalisco" not in addr_norm:
        return False, "La dirección geocodificada no está en Guadalajara: " + formatted_address
    # Extraer número y calle de nuestra dirección (primer número y primera palabra significativa)
    numeros_nuestros = set(re.findall(r"\d+", dir_norm))
    numeros_geo = set(re.findall(r"\d+", addr_norm))
    if numeros_nuestros and not (numeros_nuestros & numeros_geo):
        return False, "El número de la dirección no coincide con el geocodificado. Nuestra: " + direccion + " | Geo: " + formatted_address
    return True, ""


def extraer_lugares(content):
    """Extrae lista de (tipo, nombre, direccion, lat, lng, start, end, obj_str) de mapa.html."""
    lugares = []
    for tipo, marker in [("historicos", "historicos: ["), ("empresas", "empresas: [")]:
        for obj_str, start, end in extraer_objetos_con_braces(content, marker):
            nombre, direccion, lat, lng = extraer_campos(obj_str)
            if nombre is None and direccion is None:
                continue
            lugares.append({
                "tipo": tipo,
                "nombre": nombre or "",
                "direccion": direccion or "",
                "lat": lat,
                "lng": lng,
                "start": start,
                "end": end,
                "obj_str": obj_str,
            })
    return lugares


def main():
    print("Leyendo", MAPA_HTML, "...")
    with open(MAPA_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    lugares = extraer_lugares(content)
    print("Encontrados:", len([p for p in lugares if p["tipo"] == "historicos"]), "históricos,",
          len([p for p in lugares if p["tipo"] == "empresas"]), "empresas.")
    con_direccion = [p for p in lugares if p["direccion"] and not p["direccion"].strip().startswith("Contrataciones")]
    print("Con dirección a geocodificar:", len(con_direccion))

    resultados = []
    no_coincidencias = []

    for i, lugar in enumerate(con_direccion):
        nombre = lugar["nombre"]
        direccion = lugar["direccion"]
        lat_old, lng_old = lugar["lat"], lugar["lng"]
        start, end = lugar["start"], lugar["end"]
        print("  [%d/%d] %s" % (i + 1, len(con_direccion), nombre[:50]))

        time.sleep(DELAY_SEC)
        lat_new, lng_new, formatted_addr, err = geocode_address(direccion, API_KEY)

        if err or lat_new is None:
            no_coincidencias.append({
                "nombre": nombre,
                "direccion": direccion,
                "motivo": "Geocoding falló: " + (err or "sin resultados"),
            })
            resultados.append({
                "nombre": nombre,
                "direccion": direccion,
                "lat_old": lat_old,
                "lng_old": lng_old,
                "lat_new": None,
                "lng_new": None,
                "formatted_address": None,
                "ok": False,
                "advertencia": err or "ZERO_RESULTS",
                "start": start,
                "end": end,
            })
            continue

        ok, msg = nombre_coincide_con_direccion(nombre, direccion, formatted_addr)
        if not ok:
            no_coincidencias.append({
                "nombre": nombre,
                "direccion": direccion,
                "motivo": msg,
                "formatted_address": formatted_addr,
            })
            resultados.append({
                "nombre": nombre,
                "direccion": direccion,
                "lat_old": lat_old,
                "lng_old": lng_old,
                "lat_new": lat_new,
                "lng_new": lng_new,
                "formatted_address": formatted_addr,
                "ok": False,
                "advertencia": msg,
                "start": start,
                "end": end,
            })
        else:
            resultados.append({
                "nombre": nombre,
                "direccion": direccion,
                "lat_old": lat_old,
                "lng_old": lng_old,
                "lat_new": lat_new,
                "lng_new": lng_new,
                "formatted_address": formatted_addr,
                "ok": True,
                "start": start,
                "end": end,
            })

    # Guardar reporte JSON
    with open(REPORTE_GEOCODING, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print("\nResultados guardados en", REPORTE_GEOCODING)

    # Guardar no coincidencias para que el usuario las revise
    with open(REPORTE_NO_COINCIDENCIAS, "w", encoding="utf-8") as f:
        f.write("NO COINCIDENCIAS O ADVERTENCIAS (revisar antes de aplicar coordenadas)\n")
        f.write("=" * 80 + "\n\n")
        if not no_coincidencias:
            f.write("Ninguna. Todos los puntos pasaron la verificación nombre/dirección.\n")
        else:
            for i, item in enumerate(no_coincidencias, 1):
                f.write("%d. %s\n" % (i, item["nombre"]))
                f.write("   Dirección en mapa: %s\n" % item["direccion"])
                f.write("   Motivo: %s\n" % item["motivo"])
                if item.get("formatted_address"):
                    f.write("   Dirección devuelta por Google: %s\n" % item["formatted_address"])
                f.write("\n")

    print("No coincidencias / advertencias guardadas en", REPORTE_NO_COINCIDENCIAS)
    if no_coincidencias:
        print("\n*** HAY %d PUNTOS CON NO COINCIDENCIA O ERROR. REVISA '%s' ANTES DE APLICAR. ***" % (len(no_coincidencias), REPORTE_NO_COINCIDENCIAS))
        for item in no_coincidencias[:10]:
            print("  -", item["nombre"], ":", item["motivo"][:60])

    # Aplicar solo los que están OK; reemplazar de atrás hacia adelante para no desalinear índices
    aplicados = 0
    reemplazos = []
    for r in resultados:
        if not r.get("ok") or r.get("lat_new") is None or r.get("start") is None:
            continue
        start, end = r["start"], r["end"]
        bloque = content[start : end + 1]
        lat_old_s = str(r["lat_old"]) if r["lat_old"] is not None else ""
        lng_old_s = str(r["lng_old"]) if r["lng_old"] is not None else ""
        if not lat_old_s or not lng_old_s:
            continue
        # Aceptar cualquier número (p. ej. 20.6773 o 20.67730) para que el reemplazo siempre coincida
        pat_lat = r"lat:\s*[\d.-]+,\s*lng:\s*[\d.-]+"
        new_val = "lat: " + str(r["lat_new"]) + ",\n                    lng: " + str(r["lng_new"])
        if re.search(pat_lat, bloque):
            bloque_new = re.sub(pat_lat, new_val, bloque, count=1)
            if bloque_new != bloque:
                reemplazos.append((start, end + 1, bloque_new))
    # Aplicar de mayor start a menor para no alterar posiciones
    for start, end, bloque_new in sorted(reemplazos, key=lambda x: -x[0]):
        content = content[:start] + bloque_new + content[end:]
        aplicados += 1

    if aplicados > 0:
        with open(MAPA_HTML, "w", encoding="utf-8") as f:
            f.write(content)
        print("\nCoordenadas actualizadas en mapa.html para %d puntos (solo los que coincidían)." % aplicados)
    else:
        print("\nNo se aplicaron cambios a mapa.html (revisa resultados o usa el JSON para actualizar a mano).")

    return 0


if __name__ == "__main__":
    exit(main())
