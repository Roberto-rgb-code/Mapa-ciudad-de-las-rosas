import json
import urllib.request
import urllib.parse
import ssl

API_KEY = "AIzaSyAEH7geT5dqaXiVNJ-L4EbcTHOIrlb05gs"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = [
    "Palacio de Gobierno Guadalajara Jalisco",
    "Museo Regional de Guadalajara Calle Liceo",
    "Casa de los Perros Guadalajara Av Alcalde",
    "Casa de los Perros Guadalajara Jalisco edificio historico",
    "Av Fray Antonio Alcalde entre Reforma y San Felipe Guadalajara",
]

for q in queries:
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote(q)}&inputtype=textquery&fields=name,geometry,formatted_address&key={API_KEY}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, context=ctx)
        data = json.loads(resp.read().decode("utf-8"))
        if data.get("candidates"):
            for c in data["candidates"]:
                loc = c["geometry"]["location"]
                print(f"Query: {q}")
                print(f"  Name: {c.get('name', 'N/A')}")
                print(f"  Addr: {c.get('formatted_address', 'N/A')}")
                print(f"  Lat:  {loc['lat']}")
                print(f"  Lng:  {loc['lng']}")
                print()
        else:
            print(f"Query: {q} -> No results")
    except Exception as e:
        print(f"Query: {q} -> ERROR: {e}")
