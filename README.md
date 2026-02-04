# Mapa Guadalajara Ciudad de las Rosas

Mapa interactivo embebible de Guadalajara con puntos de interés históricos y empresas.

## Características

- 🗺️ Mapa interactivo con Google Maps
- 📍 Edificios históricos con imágenes personalizadas
- 🏢 Empresas y restaurantes georreferenciados
- 👤 Geolocalización del usuario (GPS o por IP)
- 📱 Diseño responsive y embebible con iframe

## Uso

### Ver el mapa localmente

Abre `mapa.html` en tu navegador o usa un servidor local:

```bash
# Con Python
python -m http.server 8000

# Con Node.js
npx http-server
```

Luego visita: `http://localhost:8000/mapa.html`

### Embeber en tu sitio web

```html
<iframe 
    src="mapa.html" 
    width="100%" 
    height="600" 
    frameborder="0" 
    style="border: 2px solid #8B1538; border-radius: 8px;"
    title="Mapa Guadalajara Ciudad de las Rosas">
</iframe>
```

## GitHub Pages

Para desplegar en GitHub Pages:

1. Sube todos los archivos a tu repositorio
2. Ve a Settings > Pages
3. Selecciona la rama `main` y carpeta `/root`
4. El mapa estará disponible en: `https://tu-usuario.github.io/nombre-repo/mapa.html`

## Archivos

- `mapa.html` - Mapa principal embebible
- `assets/` - Imágenes de los edificios históricos
  - `santuario.png`
  - `catedral.png`
  - `rotonda.png`
  - `mercadosanjuandedios.png`

## API Key y producción (GitHub Pages)

Este proyecto usa una API key de Google Maps. **Si el mapa se ve en blanco en producción** (por ejemplo en `https://roberto-rgb-code.github.io/Mapa-ciudad-de-las-rosas/`):

1. Entra en [Google Cloud Console → Credenciales](https://console.cloud.google.com/google/maps-apis/credentials).
2. Abre tu API key.
3. En **Restricciones de aplicación** → **Referidores HTTP**, agrega:
   - `https://roberto-rgb-code.github.io/*`
   - (y opcionalmente `http://localhost/*` para desarrollo).
4. Guarda y recarga la página del mapa.

Si no autorizas esta URL como referrer, la API rechaza las peticiones y el mapa no carga.

## Licencia

Este proyecto es propiedad de Guadalajara Ciudad de las Rosas.
