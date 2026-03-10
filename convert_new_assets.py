from PIL import Image
import os

files = [
    ('assets/CALANDRIA1.psd', 'assets/iconos-monumentos/calandrias.png'),
    ('assets/WhatsApp Image 2026-03-05 at 4.51.12 PM.jpeg', 'assets/iconos-monumentos/santa-teresa.png')
]

for src, dst in files:
    try:
        if os.path.exists(src):
            img = Image.open(src)
            img = img.convert('RGBA')
            img.save(dst, 'PNG')
            print(f'Converted {src} to {dst}')
        else:
            print(f'File {src} not found')
    except Exception as e:
        print(f'Error converting {src}: {e}')
