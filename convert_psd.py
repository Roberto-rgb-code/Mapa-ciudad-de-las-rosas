import os
import unicodedata
from PIL import Image

src_dir = "assets/Monumentos-20260223T041740Z-1-001/Monumentos"
dst_dir = "assets/iconos-monumentos"
os.makedirs(dst_dir, exist_ok=True)

name_to_png = {
    "arcos milenio": "arcos-milenio.png",
    "cabanas": "cabanas.png",
    "casa de los perros": "casa-de-los-perros.png",
    "degollado": "degollado.png",
    "santuario": "santuario.png",
    "los arcos": "los-arcos.png",
    "minerva": "minerva.png",
    "museo regional": "museo-regional.png",
    "palacio de gobierno": "palacio-gobierno.png",
    "panteon belen": "panteon-belen.png",
}

def normalize(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()

for fname in os.listdir(src_dir):
    if not fname.lower().endswith('.psd'):
        continue
    norm = normalize(fname)
    matched_png = None
    for key, png in name_to_png.items():
        if key in norm:
            matched_png = png
            break
    if not matched_png:
        print(f"SKIP (no match): {fname}")
        continue
    src_path = os.path.join(src_dir, fname)
    dst_path = os.path.join(dst_dir, matched_png)
    try:
        img = Image.open(src_path)
        img = img.convert("RGBA")
        img.save(dst_path, "PNG")
        print(f"OK: {fname} -> {matched_png} ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"ERROR: {fname} -> {e}")
