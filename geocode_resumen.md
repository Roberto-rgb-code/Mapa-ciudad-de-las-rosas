# Informe Geocodificación - Mapa GDL Rosas

**Fecha:** 22 Feb 2026  
**Lugares verificados:** 47 (13 históricos + 34 empresas) → **44 tras eliminar duplicados**

---

## 1. Duplicados eliminados

Se eliminaron **3 entradas duplicadas** (mismo punto exacto en el mapa):

| Eliminado | Mantenido | Motivo |
|-----------|-----------|--------|
| EX-CONVENTO DE SANTA TERESA | Ex Convento de Santa Teresa | Misma ubicación (C. Donato Guerra 25) |
| CASA ANGUIANO (2ª entrada) | CASA ANGUIANO Artículos Religiosos | Mismo punto (Av. Alcalde 113) |
| BIRRIERIA El Pilón de los Arrieros (2ª) | BIRRIERIA El Pilón de los Arrieros | Mismo punto (Calle Galeana 388) |

---

## 2. Resultados de geocodificación (Google API)

### OK (38 puntos)
Coordenadas dentro del umbral (< 150 m respecto a Google).

### A revisar (3 puntos)
- **Catedral de Guadalajara** – 375 m
- **Rotonda de los Jaliscienses Ilustres** – 281 m  
- **RESTAURANT Casa Dolores** (Paseo Alcalde 22) – 369 m  

### Mal ubicados según Google (6 puntos)

| Lugar | Dist. | Observación |
|-------|-------|-------------|
| **Palacio de Gobierno** | 455 m | Google devuelve Av. Ramón Corona; el Palacio está en Av. Corona. Revisar coordenadas. |
| **Glorieta de la Minerva** | 634 m | Ubicación actual posiblemente correcta (Av. López Mateos y Vallarta). |
| **Los Arcos de Guadalajara** | 1671 m | Hay varios “Arcos” en la ciudad; verificar si corresponde a Av. Vallarta o Arcos del Milenio. |
| **CALANDRIAS eléctricas** | ~600 km | Error de geocode: "Av. Hidalgo" devolvió Tampico. La coordenada actual (centro GDL) parece correcta. |
| **CASA CARRANZA Hotel** | 7266 m | Google devolvió Zapopan. Verificar "Venustiano Carranza 242, Guadalajara centro". |
| **MARIACHI México en la Piel** | 11976 m | Servicio sin dirección fija; la dirección es de contacto. Marcador en centro (aproximado). |

---

## 3. Tooltips

Las direcciones del tooltip coinciden razonablemente con los resultados de Google, salvo en los casos anteriores. **CALANDRIAS** y **MARIACHI** usan descripciones, no direcciones geocodificables.

---

## 4. Sucursales (intencionales)

Mismo nombre, distintas ubicaciones (correcto):

- **RESTAURANT Casa Dolores** – Paseo Alcalde 22 y Av. Chapultepec Sur 451  
- **TARASKA Helados y Paletas** – Morelos 99 y Ramón Corona 156  
- **RAGAZZA Fashion** – Av. Juárez 210 y Av. Vallarta 1291  

---

## Archivos generados

- `geocode_reporte.json` – Resultado detallado de cada punto  
- `geocode_check_full.py` – Script de verificación  
