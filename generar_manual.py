#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera MANUAL-CONTINUIDAD.pdf en la raíz del proyecto."""
from pathlib import Path
from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "MANUAL-CONTINUIDAD.pdf"


def _find_font(*names):
    candidates = []
    windir = Path(r"C:\Windows\Fonts")
    if windir.is_dir():
        candidates.extend(windir / n for n in names)
    for base in (Path("/Library/Fonts"), Path("/usr/share/fonts/truetype/dejavu")):
        if base.is_dir():
            candidates.extend(base / n for n in names)
    for path in candidates:
        if path.is_file():
            return str(path)
    return None


class ManualPDF(FPDF):
    def __init__(self):
        super().__init__()
        regular = _find_font("arial.ttf", "DejaVuSans.ttf")
        bold = _find_font("arialbd.ttf", "DejaVuSans-Bold.ttf")
        italic = _find_font("ariali.ttf", "DejaVuSans-Oblique.ttf")
        mono = _find_font("cour.ttf", "DejaVuSansMono.ttf")
        if not regular:
            raise FileNotFoundError("No se encontró fuente Arial/DejaVu para generar el PDF.")
        self.add_font("Body", "", regular)
        self.add_font("Body", "B", bold or regular)
        self.add_font("Body", "I", italic or regular)
        self.add_font("Mono", "", mono or regular)
        self._font = "Body"

    def footer(self):
        self.set_y(-15)
        self.set_font("Body", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def section_title(pdf, text):
    pdf.ln(4)
    pdf.set_font("Body", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 7, text)
    pdf.ln(1)


def subsection(pdf, text):
    pdf.ln(2)
    pdf.set_font("Body", "B", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, text)


def body(pdf, text):
    pdf.set_font("Body", "", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 5, text)
    pdf.ln(1)


def bullet(pdf, text):
    pdf.set_font("Body", "", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 5, f"- {text}")


def code(pdf, text):
    pdf.set_font("Mono", "", 9)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 4.5, text, fill=True)
    pdf.ln(1)


def build_pdf():
    pdf = ManualPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Portada
    pdf.set_font("Body", "B", 22)
    pdf.set_text_color(139, 21, 56)
    pdf.multi_cell(0, 10, "Mapa Guadalajara\nCiudad de las Rosas")
    pdf.ln(2)
    pdf.set_font("Body", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 7, "Manual de continuidad y edición")
    pdf.ln(4)
    pdf.set_font("Body", "", 10)
    pdf.multi_cell(
        0,
        5,
        "Documento para quien reciba el repositorio y necesite mantener, "
        "actualizar anunciantes, sitios históricos, logos o coordenadas del mapa interactivo.",
    )
    pdf.ln(6)
    body(pdf, "Repositorio: https://github.com/Roberto-rgb-code/Mapa-ciudad-de-las-rosas")
    body(pdf, "Sitio publicado (GitHub Pages): https://roberto-rgb-code.github.io/Mapa-ciudad-de-las-rosas/mapa.html")
    body(pdf, "Entrada alternativa: index.html (mismo contenido funcional que mapa.html)")

    section_title(pdf, "1. Qué es este proyecto")
    body(
        pdf,
        "Aplicación web estática (HTML + CSS + JavaScript) que muestra un mapa interactivo "
        "de Guadalajara con Google Maps. Incluye:",
    )
    bullet(pdf, "Sidebar izquierdo: anunciantes numerados 1-25 (mapa impreso jun-jul).")
    bullet(pdf, "Sidebar / seccion historica: sitios con letras A-I visibles en lista.")
    bullet(pdf, "Pins en el mapa: números crema (empresas) e iconos ilustrados (históricos).")
    bullet(pdf, "Carrusel inferior de logos (25 paneles, uno por anunciante).")
    bullet(pdf, "Tooltips con dirección, teléfono, galería, Street View y rutas.")
    bullet(pdf, "Traducción parcial al inglés (botón en sidebar).")

    section_title(pdf, "2. Estructura del repositorio")
    code(
        pdf,
        "Mapa GDL Rosas/\n"
        "  index.html          Mapa completo (mantener sincronizado con mapa.html)\n"
        "  mapa.html           Versión embebible / producción\n"
        "  assets/             Imágenes, logos, iconos de monumentos\n"
        "  geocode_lugares.py  Geocodificar direcciones vía Google API\n"
        "  geocode_abril2026.py Geocodificación puntual (utilidad)\n"
        "  README.md           Resumen breve del proyecto\n"
        "  MANUAL-CONTINUIDAD.pdf  Este manual\n"
        "  generar_manual.py   Regenera el PDF\n"
        "  node_modules/       Dependencias opcionales (PSD/sharp); no necesarias para el mapa",
    )
    body(
        pdf,
        "IMPORTANTE: index.html y mapa.html deben editarse juntos. Hoy solo difieren en un "
        "comentario HTML; todo lo demás (datos, carrusel, estilos, scripts) es el mismo.",
    )

    section_title(pdf, "3. Dónde viven los datos")
    body(
        pdf,
        "Todo el contenido editable está dentro de index.html / mapa.html, en el objeto JavaScript "
        "const lugares = { historicos: [...], empresas: [...] } (aprox. línea 3922).",
    )
    subsection(pdf, "3.1 Sitios históricos (lugares.historicos)")
    body(pdf, "Cada objeto puede incluir:")
    code(
        pdf,
        "nombre, lat, lng, categoria, descripcion, direccion, imagen,\n"
        "streetViewLat, streetViewLng, streetViewHeading, streetViewPitch,\n"
        "ocultoEnSidebar: true   // pin en mapa, sin fila en sidebar\n"
        "sinMarcadorEnMapa: true // solo datos, sin pin (raro en históricos)",
    )
    body(
        pdf,
        "Los históricos visibles en sidebar reciben letras A, B, C… en orden del array. "
        "CALANDRIAS eléctricas se excluye de la lista. Los marcados ocultoEnSidebar "
        "conservan su letra interna pero no aparecen en el sidebar.",
    )

    subsection(pdf, "3.2 Anunciantes / empresas (lugares.empresas)")
    code(
        pdf,
        "nombre, lat, lng, categoria, descripcion, direccion,\n"
        "telefono, facebook, instagram, web, email, horario, galeria: [...],\n"
        "sinMarcadorEnMapa: true   // en datos pero sin pin rojo/crema\n"
        "streetViewLat, streetViewLng, streetViewHeading, ...",
    )

    section_title(pdf, "4. Numeración 1–25 (mapa impreso)")
    body(
        pdf,
        "La numeración visible NO sigue el índice del array empresas. Se controla con "
        "ordenAnunciantes y etiquetasAnunciantes (aparecen 3 veces: sidebar, mapa y deben "
        "coincidir con el carrusel).",
    )
    code(
        pdf,
        "var ordenAnunciantes = [\n"
        "  'GUARDIÁN CAFÉ-GALERÍA', 'TORTAS AHOGADAS Las Famosas', ...\n"
        "];\n"
        "var etiquetasAnunciantes = [1,2,3,...,25];",
    )
    body(pdf, "Reglas importantes:")
    bullet(pdf, "Mismo nombre repetido = sucursales (ej. Casa Dolores #5 y #6, Ragazza #10 y #11).")
    bullet(pdf, "CASA San Matías tiene dos pins en mapa (#12) pero una sola entrada en ordenAnunciantes; el código asigna número 12 a ambas empresas con ese nombre.")
    bullet(pdf, "Empresas en el array pero NO en ordenAnunciantes quedan ocultas del mapa si son duplicados de nombre; o sin número si son extras.")
    bullet(pdf, "sinMarcadorEnMapa oculta el pin aunque exista en datos (Pilón, Paceños, El Mesón, etc.).")

    section_title(pdf, "5. Cómo agregar o cambiar un anunciante")
    subsection(pdf, "Paso A — Datos en lugares.empresas")
    body(pdf, "Agregar o editar el objeto con nombre exacto, lat/lng y direccion.")
    subsection(pdf, "Paso B — Orden y número")
    body(pdf, "Actualizar ordenAnunciantes y etiquetasAnunciantes en:")
    bullet(pdf, "fillSidebarListFromLugares (sidebar)")
    bullet(pdf, "ordenAnunciantesMap (pins del mapa)")
    subsection(pdf, "Paso C — Carrusel HTML")
    body(
        pdf,
        "Buscar <section class=\"anunciantes-strip\">. Cada panel es un <a class=\"anuncio-panel\"> "
        "con data-marker-index = historicos.length + índice en lugares.empresas.",
    )
    body(
        pdf,
        "Ejemplo: si hay 25 históricos y la empresa está en empresas[33], el índice del "
        "marcador es 25 + 33 = 58. El carrusel muestra solo la imagen (anuncio-img-wrap); "
        "sin imagen el cuadro queda vacío.",
    )
    subsection(pdf, "Paso D — Traducciones (opcional)")
    body(pdf, "En window.T.en.sidebarLeftNames y bloques de traducción del tooltip (~línea 3300).")

    section_title(pdf, "6. Coordenadas (lat/lng)")
    body(
        pdf,
        "Usar Google Maps: clic derecho en el lugar → coordenadas, o los scripts Python incluidos.",
    )
    subsection(pdf, "geocode_lugares.py")
    code(
        pdf,
        "set GOOGLE_MAPS_API_KEY=tu_clave   (Windows)\n"
        "py -3 geocode_lugares.py",
    )
    body(pdf, "Lee mapa.html, geocodifica direcciones y puede actualizar lat/lng automáticamente.")
    subsection(pdf, "geocode_abril2026.py")
    body(pdf, "Script simple para probar direcciones puntuales editando la lista addrs al final.")

    section_title(pdf, "7. API Key de Google Maps")
    body(pdf, "La clave está al final de index.html / mapa.html en la URL del script de Maps.")
    body(pdf, "APIs necesarias: Maps JavaScript API, Geocoding API, Places (opcional), Street View.")
    body(pdf, "Para GitHub Pages, en Google Cloud Console → Credenciales → Restricciones HTTP:")
    code(
        pdf,
        "https://roberto-rgb-code.github.io/*\n"
        "http://localhost/*",
    )
    body(
        pdf,
        "Si el mapa carga en blanco en producción, casi siempre es restricción de referrer "
        "o facturación desactivada en el proyecto de Google Cloud.",
    )

    section_title(pdf, "8. Assets e imágenes")
    body(pdf, "Carpetas habituales:")
    bullet(pdf, "assets/Logos/ — logos de anunciantes para carrusel y tooltips")
    bullet(pdf, "assets/iconos-monumentos/ — iconos de sitios históricos en el mapa")
    bullet(pdf, "assets/Anuncios/ — material promocional / galerías")
    bullet(pdf, "assets/neuvos logos v2/ — logos recientes")
    bullet(pdf, "assets/fotos-anunciantes/ — galerías por negocio")
    body(
        pdf,
        "Usar rutas relativas con %20 para espacios (ej. assets/Logos/Alma%20Jalisco.png). "
        "Formatos: PNG/JPEG/WebP. Mantener proporción cuadrada ~100×100 px para carrusel.",
    )

    section_title(pdf, "9. Probar en local")
    code(
        pdf,
        "cd \"Mapa GDL Rosas\"\n"
        "py -3 -m http.server 8000\n"
        "Abrir: http://localhost:8000/mapa.html",
    )
    body(
        pdf,
        "No abrir el HTML con doble clic (file://) si quieres probar geolocalización o "
        "evitar problemas de rutas; usa siempre un servidor local.",
    )

    section_title(pdf, "10. Publicar cambios")
    body(pdf, "Flujo recomendado:")
    bullet(pdf, "Editar index.html")
    bullet(pdf, "Copiar index.html → mapa.html (o usar el script de sync del repo)")
    bullet(pdf, "Probar en localhost")
    bullet(pdf, "git add, commit, push a master")
    bullet(pdf, "GitHub Pages actualiza en 1–3 minutos")
    body(pdf, "Embeber en otro sitio:")
    code(
        pdf,
        '<iframe src="https://roberto-rgb-code.github.io/Mapa-ciudad-de-las-rosas/mapa.html"\n'
        '  width="100%" height="600" frameborder="0"\n'
        '  title="Mapa Guadalajara Ciudad de las Rosas"></iframe>',
    )

    section_title(pdf, "11. Casos especiales documentados")
    bullet(pdf, "#5 y #6 Casa Dolores: Paseo Alcalde 22 (centro) e Independencia 151 El Parián (Tlaquepaque).")
    bullet(pdf, "#12 Casa San Matías: dos pins (Alberta 1509 y Chapultepec 256-B), un panel en carrusel.")
    bullet(pdf, "#13 Alma Jalisco y #20 Rosticerías Rizo: juntos en Mercado Corona, 1er piso.")
    bullet(pdf, "#22 Raspados Jalisco: esquina Juan Manuel y Calz. Independencia Nte., frente Parque Morelos.")
    bullet(pdf, "Anunciantes fuera del mapa impreso: sinMarcadorEnMapa (no borrar datos, solo ocultar pin).")

    section_title(pdf, "12. Errores frecuentes")
    bullet(pdf, "Pin con número incorrecto → revisar ordenAnunciantesMap y nombre exacto en empresas.")
    bullet(pdf, "Clic en carrusel no centra el mapa → data-marker-index desincronizado con índice real.")
    bullet(pdf, "Cuadro vacío en carrusel → falta <div class=\"anuncio-img-wrap\"> con <img>.")
    bullet(pdf, "Dos pins duplicados sin número → empresa extra con mismo nombre sin entrada en orden.")
    bullet(pdf, "Mapa en blanco en producción → restricción API key o cuota Google Cloud.")

    section_title(pdf, "13. Checklist antes de entregar cambios")
    bullet(pdf, "25 paneles en carrusel con logo visible")
    bullet(pdf, "Sidebar 1–25 coincide con mapa impreso")
    bullet(pdf, "index.html y mapa.html sincronizados")
    bullet(pdf, "Pins probados visualmente vs mapa impreso o Google Maps")
    bullet(pdf, "Commit con mensaje claro; push a origin/master")

    section_title(pdf, "14. Regenerar este manual")
    code(pdf, "py -3 generar_manual.py")
    body(pdf, "Genera MANUAL-CONTINUIDAD.pdf en la raíz del proyecto.")

    pdf.ln(4)
    pdf.set_font("Body", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        "Manual generado automáticamente. Proyecto: Guadalajara Ciudad de las Rosas. "
        "Para dudas técnicas sobre Google Maps: console.cloud.google.com",
    )

    pdf.output(str(OUTPUT))
    print(f"Generado: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
