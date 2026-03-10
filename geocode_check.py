import json
import re
import urllib.request
import urllib.parse
import ssl
import time

API_KEY = "AIzaSyBNkRTHRBGK6YZqa34DmiZfEzc3bRynnd0"

with open("mapa.html", "r", encoding="utf-8") as f:
    html = f.read()

pattern = r'nombre:\s*"([^"]+)",\s*\n\s*lat:\s*([\d.\-]+),\s*\n\s*lng:\s*([\d.\-]+),\s*\n\s*categoria:\s*"([^"]+)"'
markers = re.findall(pattern, html)

# Only check historicos (first section before empresas)
hist_section = html.split("historicos:")[1].split("empresas:")[0]
hist_markers = re.findall(pattern, hist_section)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

results = []
for nombre, lat, lng, cat in hist_markers:
    query = f"{nombre}, Guadalajara, Jalisco, Mexico"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(query)}&key={API_KEY}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
        if data["status"] == "OK" and data["results"]:
            loc = data["results"][0]["geometry"]["location"]
            g_lat, g_lng = loc["lat"], loc["lng"]
            cur_lat, cur_lng = float(lat), float(lng)
            dlat = abs(g_lat - cur_lat)
            dlng = abs(g_lng - cur_lng)
            dist_approx_m = ((dlat**2 + dlng**2)**0.5) * 111000
            status = "OK" if dist_approx_m < 300 else "REVISAR"
            results.append({
                "nombre": nombre,
                "actual": [cur_lat, cur_lng],
                "google": [g_lat, g_lng],
                "dist_m": round(dist_approx_m),
                "status": status,
                "formatted": data["results"][0].get("formatted_address", "")
            })
            print(f"{status:8s} | {dist_approx_m:6.0f}m | {nombre}")
            if status == "REVISAR":
                print(f"         | actual: {cur_lat}, {cur_lng}")
                print(f"         | google: {g_lat}, {g_lng}")
                print(f"         | addr:   {data['results'][0].get('formatted_address', '')}")
        else:
            print(f"NO_FOUND |        | {nombre} -> {data['status']}")
            results.append({"nombre": nombre, "status": "NO_FOUND"})
    except Exception as e:
        print(f"ERROR    |        | {nombre} -> {e}")
        results.append({"nombre": nombre, "status": "ERROR", "error": str(e)})
    time.sleep(0.2)

with open("geocode_diagnostico.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(results)} marcadores verificados")
print(f"A revisar: {sum(1 for r in results if r.get('status') == 'REVISAR')}")
