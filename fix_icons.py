import os
from PIL import Image
import numpy as np

icon_dir = "assets/iconos-monumentos"

for fname in os.listdir(icon_dir):
    if not fname.endswith('.png'):
        continue
    path = os.path.join(icon_dir, fname)
    img = Image.open(path).convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Make near-white pixels transparent (threshold ~240)
    white_mask = (r > 235) & (g > 235) & (b > 235)
    data[white_mask, 3] = 0

    # Also handle very light gray areas at edges
    light_mask = (r > 220) & (g > 220) & (b > 220) & (abs(r.astype(int) - g.astype(int)) < 15) & (abs(g.astype(int) - b.astype(int)) < 15)
    data[light_mask, 3] = 0

    result = Image.fromarray(data)

    # Crop to content (trim transparent edges)
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)

    result.save(path, "PNG")
    print(f"OK: {fname} -> {result.size[0]}x{result.size[1]}")
