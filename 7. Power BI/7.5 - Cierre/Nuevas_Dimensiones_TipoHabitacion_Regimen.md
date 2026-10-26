# Nuevas dimensiones: Tipo de Habitación y Régimen

> Extensión del star schema de HotelesMediterraneum.  
> Las tablas se construyen automáticamente extrayendo los valores reales de `reservas`.  
> Implementación manual en Power BI Desktop: **Modeling → New Table** → pegar el DAX.

---

## Por qué estas dos dimensiones

| Columna actual | Problema | Solución |
|---|---|---|
| `reservas[room_type]` | Texto repetido en cada fila, sin atributos, sin filtro limpio | `dim_tipo_habitacion` con categoría y capacidad |
| `reservas[meal_plan]` | Igual — y la medida `Noches All Inclusive` ya demuestra que hay demanda analítica | `dim_regimen` con código, comidas incluidas y nivel de precio |

Con estas dos dimensiones el star schema queda completo para el análisis de producto hotelero:

```
                    dim_tipo_habitacion
                           │
dim_hotel ── reservas ── dim_channel
                  │
              dim_regimen
                  │
             Calendario
```

---

## PASO 1 — Crear dim_tipo_habitacion

En Power BI Desktop: pestaña **Modeling → New Table** → pegar el siguiente DAX:

```dax
dim_tipo_habitacion =
ADDCOLUMNS(
    DISTINCT(reservas[room_type]),
    "categoria",
        SWITCH(
            reservas[room_type],
            "Suite",             "Premium",
            "Junior Suite",      "Premium",
            "Penthouse",         "Premium",
            "Deluxe",            "Superior",
            "Superior",          "Superior",
            "Deluxe Superior",   "Superior",
            "Standard Superior", "Estándar",
            "Standard",          "Estándar",
            "Economy",           "Económica",
            "Family",            "Familiar",
            "Family Suite",      "Familiar",
            "Bungalow",          "Especial",
            "Villa",             "Especial",
            "Estándar"
        ),
    "capacidad_max",
        SWITCH(
            reservas[room_type],
            "Suite",             2,
            "Junior Suite",      2,
            "Penthouse",         4,
            "Deluxe",            2,
            "Superior",          2,
            "Deluxe Superior",   3,
            "Standard Superior", 3,
            "Standard",          2,
            "Economy",           1,
            "Family",            4,
            "Family Suite",      6,
            "Bungalow",          4,
            "Villa",             8,
            2
        ),
    "orden_categoria",
        SWITCH(
            reservas[room_type],
            "Suite",             5,
            "Junior Suite",      4,
            "Penthouse",         5,
            "Deluxe",            4,
            "Superior",          3,
            "Deluxe Superior",   4,
            "Standard Superior", 2,
            "Standard",          2,
            "Economy",           1,
            "Family",            3,
            "Family Suite",      4,
            "Bungalow",          3,
            "Villa",             5,
            2
        )
)
```

> **Nota:** las columnas `categoria` y `capacidad_max` usan los valores típicos del sector.
> Si tu CSV tiene nombres diferentes en `room_type` (por ejemplo "Habitación Doble" en lugar de "Standard"),
> ajusta los literales del SWITCH para que coincidan exactamente con tus datos.
> Puedes ver los valores reales ejecutando en DAX Studio:
> `EVALUATE DISTINCT(reservas[room_type])`

### Configurar la columna `categoria` como sortByColumn

Después de crear la tabla, en la vista **Model**:
1. Seleccionar `dim_tipo_habitacion[categoria]`
2. Panel de propiedades → **Sort by column** → `orden_categoria`
3. Ocultar `orden_categoria` (clic derecho → Hide)

---

## PASO 2 — Crear dim_regimen

En Power BI Desktop: pestaña **Modeling → New Table** → pegar el siguiente DAX:

```dax
dim_regimen =
ADDCOLUMNS(
    DISTINCT(reservas[meal_plan]),
    "codigo",
        SWITCH(
            reservas[meal_plan],
            "Room Only",             "RO",
            "Solo Alojamiento",      "RO",
            "Bed and Breakfast",     "BB",
            "Bed & Breakfast",       "BB",
            "Alojamiento Desayuno",  "BB",
            "Half Board",            "HB",
            "Half-Board",            "HB",
            "Media Pension",         "HB",
            "Media Pensión",         "HB",
            "Full Board",            "FB",
            "Full-Board",            "FB",
            "Pension Completa",      "FB",
            "Pensión Completa",      "FB",
            "All Inclusive",         "AI",
            "All-Inclusive",         "AI",
            "Todo Incluido",         "AI",
            "?"
        ),
    "incluye_desayuno",
        NOT reservas[meal_plan] IN {"Room Only", "Solo Alojamiento"},
    "incluye_almuerzo",
        reservas[meal_plan] IN {
            "Full Board", "Full-Board", "Pension Completa", "Pensión Completa",
            "All Inclusive", "All-Inclusive", "Todo Incluido"
        },
    "incluye_cena",
        reservas[meal_plan] IN {
            "Half Board", "Half-Board", "Media Pension", "Media Pensión",
            "Full Board", "Full-Board", "Pension Completa", "Pensión Completa",
            "All Inclusive", "All-Inclusive", "Todo Incluido"
        },
    "nivel_precio",
        SWITCH(
            reservas[meal_plan],
            "Room Only",             1,
            "Solo Alojamiento",      1,
            "Bed and Breakfast",     2,
            "Bed & Breakfast",       2,
            "Alojamiento Desayuno",  2,
            "Half Board",            3,
            "Half-Board",            3,
            "Media Pension",         3,
            "Media Pensión",         3,
            "Full Board",            4,
            "Full-Board",            4,
            "Pension Completa",      4,
            "Pensión Completa",      4,
            "All Inclusive",         5,
            "All-Inclusive",         5,
            "Todo Incluido",         5,
            1
        ),
    "etiqueta_nivel",
        SWITCH(
            reservas[meal_plan],
            "Room Only",             "⬜ Solo alojamiento",
            "Solo Alojamiento",      "⬜ Solo alojamiento",
            "Bed and Breakfast",     "🟡 Con desayuno",
            "Bed & Breakfast",       "🟡 Con desayuno",
            "Alojamiento Desayuno",  "🟡 Con desayuno",
            "Half Board",            "🟠 Media pensión",
            "Half-Board",            "🟠 Media pensión",
            "Media Pension",         "🟠 Media pensión",
            "Media Pensión",         "🟠 Media pensión",
            "Full Board",            "🔴 Pensión completa",
            "Full-Board",            "🔴 Pensión completa",
            "Pension Completa",      "🔴 Pensión completa",
            "Pensión Completa",      "🔴 Pensión completa",
            "All Inclusive",         "🟢 Todo incluido",
            "All-Inclusive",         "🟢 Todo incluido",
            "Todo Incluido",         "🟢 Todo incluido",
            "❓ Otro"
        )
)
```

### Configurar sortByColumn en `etiqueta_nivel`

1. Seleccionar `dim_regimen[etiqueta_nivel]`
2. **Sort by column** → `nivel_precio`
3. Ocultar `nivel_precio`

---

## PASO 3 — Crear las relaciones

En la vista **Model**, crear dos relaciones arrastrando columnas:

| Desde (Many) | Hacia (One) | Dirección filtro | Activa |
|---|---|---|---|
| `reservas[room_type]` | `dim_tipo_habitacion[room_type]` | Single (→) | Sí |
| `reservas[meal_plan]` | `dim_regimen[meal_plan]` | Single (→) | Sí |

> Las relaciones son texto-a-texto — Power BI las admite perfectamente para dimensiones pequeñas.
> No es necesario crear columnas FK enteras.

---

## PASO 4 — Ocultar columnas originales de reservas

Una vez creadas las relaciones, ocultar (no eliminar) en la tabla `reservas`:

- `room_type` — ahora accesible como `dim_tipo_habitacion[room_type]`
- `meal_plan` — ahora accesible como `dim_regimen[meal_plan]`

Clic derecho sobre cada columna en el panel Fields → **Hide**.

---

## PASO 5 — Medidas nuevas que aprovechan las dimensiones

Añadir en `_Medidas`, carpeta `02 - Análisis`:

```dax
-- Revenue por tipo de habitación (contexto de la dimensión)
Revenue por Tipo Hab =
CALCULATE([Revenue Neto])
-- Usar en gráficos con dim_tipo_habitacion en el eje; no requiere código adicional.
-- La relación ya propaga el filtro automáticamente.
```

```dax
-- ADR promedio por régimen
ADR por Régimen =
DIVIDE(
    CALCULATE([Revenue Neto]),
    CALCULATE([Noches Vendidas])
)
```

```dax
-- % Revenue All Inclusive sobre total
Revenue AI % =
VAR _ai = CALCULATE([Revenue Neto], dim_regimen[codigo] = "AI")
RETURN
    DIVIDE(_ai, CALCULATE([Revenue Neto], ALL(dim_regimen)))
```

```dax
-- Cancellation Rate por tipo de habitación
Cancellation Rate Tipo Hab =
CALCULATE([Cancellation Rate])
-- igual que Revenue por Tipo Hab — la relación hace el trabajo
```

```dax
-- Reservas por categoría de habitación
Reservas Categoria Premium =
CALCULATE(
    [Reservas Totales],
    dim_tipo_habitacion[categoria] = "Premium"
)
```

```dax
-- Revenue medio por nivel de régimen (cuánto más caro el régimen, más revenue?)
Revenue por Nivel Regimen =
DIVIDE([Revenue Neto], AVERAGE(dim_regimen[nivel_precio]))
```

---

## PASO 6 — Actualizar el dashboard

### Slicers nuevos a añadir en todas las páginas relevantes

| Slicer | Campo | Páginas |
|---|---|---|
| Tipo de habitación | `dim_tipo_habitacion[room_type]` o `[categoria]` | 1, 3 |
| Régimen | `dim_regimen[etiqueta_nivel]` | 1, 3, 4 |

### Visualizaciones nuevas sugeridas

**En Página 3 — Rendimiento de Hoteles, añadir fila nueva:**

*Gráfico izquierdo — Revenue por tipo de habitación:*
- Tipo: Treemap o Bar chart
- Grupo: `dim_tipo_habitacion[categoria]`
- Valores: `[Revenue Neto]`
- Título: "Revenue por categoría de habitación"

*Gráfico derecho — Mix de régimen:*
- Tipo: Stacked bar chart
- Eje Y: `dim_hotel[country]`
- Leyenda: `dim_regimen[etiqueta_nivel]`
- Valores: `[Reservas Totales]`
- Título: "Mix de régimen por país"

**En Página 4 — Cancelaciones, añadir análisis de producto:**

*Nuevo gráfico — Cancellation Rate por tipo de habitación:*
- Tipo: Bar chart horizontal
- Eje Y: `dim_tipo_habitacion[room_type]`
- Valores: `[Cancellation Rate]`
- Formato condicional: escala verde→rojo
- Título: "Tasa de cancelación por tipo de habitación"

*Nuevo gráfico — Cancellation Rate por régimen:*
- Tipo: Bar chart horizontal
- Eje Y: `dim_regimen[etiqueta_nivel]` (ordenado por `nivel_precio`)
- Valores: `[Cancellation Rate]`
- Título: "Tasa de cancelación por régimen"

---

## Checklist de implementación

- [ ] Tabla `dim_tipo_habitacion` creada (Modeling → New Table)
- [ ] `categoria` ordenada por `orden_categoria` · `orden_categoria` oculta
- [ ] Tabla `dim_regimen` creada (Modeling → New Table)
- [ ] `etiqueta_nivel` ordenada por `nivel_precio` · `nivel_precio` oculto
- [ ] Relación `reservas[room_type]` → `dim_tipo_habitacion[room_type]` creada
- [ ] Relación `reservas[meal_plan]` → `dim_regimen[meal_plan]` creada
- [ ] `reservas[room_type]` y `reservas[meal_plan]` ocultos en el panel Fields
- [ ] Medidas nuevas creadas en `_Medidas` carpeta `02 - Análisis`
- [ ] Slicers de tipo de habitación y régimen añadidos al dashboard
- [ ] Archivo guardado como `HotelesMediterraneum_7.5.2_resuelto_FINAL.pbix`

---

## Star schema final del modelo

```
                 dim_tipo_habitacion
                 (room_type, categoria,
                  capacidad_max)
                        │
                        │ room_type
                        │
dim_hotel ──────── reservas ──────── dim_channel
(hotel_id,    (tabla de hechos)    (channel_id,
hotel_name,         │                channel)
country,            │ meal_plan
city)               │
                    │
              dim_regimen
              (meal_plan, codigo,
               incluye_desayuno,
               incluye_cena,
               nivel_precio)
                    │
               Calendario
               (Date, Año, Mes,
                Temporada, ...)
```

6 tablas · 2 relaciones nuevas · star schema completo para análisis de producto hotelero.

---

*Extensión del modelo HotelesMediterraneum · Bloque 7 Power BI*
