# Quitar polígonos de comunidades de mapa.html
with open('mapa.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar líneas de inicio y fin
inicio = None
fin = None
for i, line in enumerate(lines):
    if '// ===== POLÍGONOS DE LAS 11 COMUNIDADES DE GUADALAJARA =====' in line:
        inicio = i
    if '// ===== ETIQUETAS DE ZONAS ESTILO VINTAGE =====' in line and inicio is not None:
        fin = i
        break

if inicio and fin:
    # Eliminar las líneas de polígonos (mantener solo las líneas vacías previas)
    nuevas_lineas = lines[:inicio] + lines[fin:]
    
    with open('mapa.html', 'w', encoding='utf-8') as f:
        f.writelines(nuevas_lineas)
    
    print(f"Eliminadas líneas {inicio+1} a {fin}")
else:
    print("No se encontraron los marcadores")
