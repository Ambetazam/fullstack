# Layout Ejercicio Dos - Tema Restaurante

La estructura de la página ocupa el **100% de ancho** y **100vh de alto**. Ahora está maquetada **exclusivamente usando Flexbox y Box Model**.

## Medidas y Proporciones:

- **Contenedor Principal (body):**
  - Ancho: `100%`
  - Alto: `100vh`

- **Header (Menú Lateral Izquierdo):**
  - Ancho: `25%`
  - Alto: `100%` (equivale a `100vh` directos)

- **Main (Contenido Principal Derecho):**
  - Ancho: `75%`
  - Alto: `80%` (equivale a `80vh`)
  - Comportamiento: `display: flex; flex-direction: column;`
  
  *El `main` contiene dos secciones divididas verticalmente (flexbox):*
  - **Sección Hero (superior):**
    - Ancho: `100%` (del ancho de main)
    - Alto: `60%` (del alto de main, equivale a `48vh`)
    - *Nota: esta sección aloja un bloque de texto (`40%` ancho) y una imagen (`60%` ancho) lado a lado.*
  - **Sección Features (inferior):**
    - Ancho: `100%` (del ancho de main)
    - Alto: `40%` (del alto de main, equivale a `32vh`)
    - *Nota: dividida en dos cajas exactamente iguales (`50%` de ancho cada una).*

- **Footer (Parte inferior derecha):**
  - Ancho: `75%`
  - Alto: `20%` (equivale a `20vh`)
  - Al estar el flex en modo columna, este footer se ubica justo debajo del `main` en la segunda columna, completando los `100vh` de la parte derecha (`80vh` del main + `20vh` del footer = `100vh`).

## Paleta de Colores (Basada en Diseño Final):

- **Fondos Oscuros (Menú y Paneles):** `#111111` / `#222222` (Negro y gris muy oscuro)
- **Color de Acento (Títulos):** `#D4AF37` (Dorado elegante)
- **Texto Principal:** `#FFFFFF` (Blanco)
- **Texto Secundario:** `#9CA3AF` (Gris claro)
