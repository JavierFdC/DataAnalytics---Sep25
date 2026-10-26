# Diseño del Cuadro de Mando — HotelesMediterraneum

> Guía de implementación manual para Power BI Desktop.  
> Modelo base: `HotelesMediterraneum_7.3.1_resuelto.pbix` · 32 medidas · 5 tablas · Star schema

---

## Antes de empezar: preparar el modelo

### Medidas a crear manualmente (3 pendientes)

En Power BI Desktop → pestaña **Modeling → New Measure**, tabla `_Medidas`:

```dax
-- Carpeta: 01 - KPIs Base
RevPAR =
VAR _dias   = COUNTROWS(ALLSELECTED(Calendario))
VAR _hoteles = COUNTROWS(ALLSELECTED(dim_hotel))
RETURN
    DIVIDE([Revenue Neto], _dias * _hoteles * 50)
-- Nota: asume 50 hab/hotel. Actualizar cuando haya columna real de capacidad.
```

```dax
-- Carpeta: 03 - Time Intelligence
Reservas YTD =
CALCULATE([Reservas Totales], DATESYTD(Calendario[Date]))
```

```dax
-- Carpeta: 02 - Análisis
Hoteles Activos = DISTINCTCOUNT(reservas[hotel_id])
```

### Columna calculada a crear (tabla reservas)

```dax
-- Tabla: reservas · para la página de Cancelaciones
Tramo Lead Time =
VAR _lt = DATEDIFF(reservas[booking_date], reservas[checkin_date], DAY)
RETURN
    SWITCH(
        TRUE(),
        _lt <= 7,   "1 · 0-7 días",
        _lt <= 30,  "2 · 8-30 días",
        _lt <= 90,  "3 · 31-90 días",
        _lt <= 180, "4 · 91-180 días",
                    "5 · +180 días"
    )
```

### Ajustes de columnas recomendados

| Tabla | Columna | Acción |
|---|---|---|
| `reservas` | `booking_id`, `customer_id`, `customer_name`, `customer_email`, `is_cancelled`, `hotel_id`, `channel_id` | Ocultar (clic derecho → Hide) |
| `reservas` | `revenue`, `nights`, `adults`, `children` | Summarize by → Don't summarize |
| `dim_hotel` | `hotel_id` | Ocultar |
| `dim_hotel` | `country` | Data category → Country |
| `dim_hotel` | `city` | Data category → City |
| `dim_channel` | `channel_id` | Ocultar |
| `Calendario` | `Mes`, `Semana Año`, `Día Semana` | Ocultar |
| `Calendario` | `Año Mes` | Sort by column → *(crear columna `Año Mes Num = Año*100+Mes` oculta primero)* |

---

## Paleta de colores

| Elemento | Hex | Uso |
|---|---|---|
| España | `#0053A0` | Color de serie, mapas |
| Italia | `#009246` | Color de serie, mapas |
| Grecia | `#0D5EAF` | Color de serie, mapas |
| Positivo / crecimiento | `#1DB954` | Flechas YoY ↑, KPIs buenos |
| Negativo / cancelación | `#E63946` | Flechas YoY ↓, tasas altas |
| Fondo de página | `#F4F6F9` | Canvas de todas las páginas |
| Fondo de tarjeta | `#FFFFFF` | Cards y paneles |
| Texto principal | `#1A1A2E` | Títulos y etiquetas |
| Texto secundario | `#6B7280` | Subtítulos y descripciones |
| Línea separadora | `#E5E7EB` | Bordes y divisores |

**Tema**: aplicar el color de fondo de página en **View → Page background → Color `#F4F6F9`**.

---

## Estructura del informe

| Página | Nombre | Audiencia | Propósito |
|---|---|---|---|
| 1 | Vista Ejecutiva | CEO, CFO, directores | Resumen de negocio en un vistazo |
| 2 | Análisis Temporal | Revenue Managers | Tendencias y comparativas YoY |
| 3 | Rendimiento de Hoteles | Directores de área | Ranking y comparativa entre propiedades |
| 4 | Análisis de Cancelaciones | Revenue Managers, Operaciones | Patrón y causa de cancelaciones |

---

## Página 1 — Vista Ejecutiva

### Layout (4 franjas horizontales)

```
┌─────────────────────────────────────────────────────────────────┐
│  SLICER Año │ SLICER País │ SLICER Canal │ SLICER Temporada     │  ← franja 1 (slicers)
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│ Revenue  │  ADR     │Reservas  │  Noches  │  Cancellation      │  ← franja 2 (KPI cards)
│  Neto    │          │Totales   │ Vendidas │     Rate           │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │                              │
│   Línea: Revenue mensual         │   Barras: Revenue por país   │  ← franja 3
│   vs. año anterior               │                              │
│                                  │                              │
├──────────────┬───────────────────┴──────────────────────────────┤
│              │                                │                  │
│  Donut       │   Mapa geográfico              │  Top 10 hoteles  │  ← franja 4
│  Canales     │                                │  (barras horiz.) │
│              │                                │                  │
└──────────────┴────────────────────────────────┴──────────────────┘
```

### Franja 1 — Slicers

| Visual | Tipo | Campo | Configuración |
|---|---|---|---|
| Año | Slicer → Dropdown | `Calendario[Año]` | Single select · sin cabecera |
| País | Slicer → Lista | `dim_hotel[country]` | Multi-select · mostrar "Seleccionar todo" |
| Canal | Slicer → Lista | `dim_channel[channel]` | Multi-select |
| Temporada | Slicer → Lista | `Calendario[Temporada]` | Multi-select |

### Franja 2 — KPI Cards

| Tarjeta | Medida principal | Medida comparación | Formato |
|---|---|---|---|
| Revenue Neto | `[Revenue Neto]` | `[Revenue YoY %]` | `€ #,##0` · flecha condicional |
| ADR | `[ADR]` | `[ADR YoY %]` | `€ #,##0.00` · flecha condicional |
| Reservas Totales | `[Reservas Totales]` | `[Reservas Año Anterior]` | `#,##0` |
| Noches Vendidas | `[Noches Vendidas]` | — | `#,##0` |
| Cancellation Rate | `[Cancellation Rate]` | — | `0.0%` · semáforo (verde <15 %, amarillo <25 %, rojo ≥25 %) |

> **New Card visual (recomendado):** usar el visual "Card (new)" que permite mostrar la medida principal y la de referencia con formato diferenciado.

### Franja 3 — Gráficos principales

#### Gráfico izquierdo: Línea temporal (60 % del ancho)
- **Tipo:** Line chart  
- **Eje X:** `Calendario[Año Mes]`  
- **Valores línea 1:** `[Revenue Neto]` — color `#0053A0`, grosor 2px  
- **Valores línea 2:** `[Revenue Año Anterior]` — color `#9CA3AF`, grosor 1px, punteada  
- **Tooltip adicional:** `[Revenue YoY %]`  
- **Título:** "Revenue mensual vs. año anterior"  
- **Sin leyenda integrada** → usar anotación de texto

#### Gráfico derecho: Revenue por país (40 % del ancho)
- **Tipo:** Clustered bar chart (horizontal)  
- **Eje Y:** `dim_hotel[country]`  
- **Valores:** `[Revenue Neto]`  
- **Etiquetas de datos:** activadas, formato `€ #,##0`  
- **Color por país:** España=`#0053A0`, Italia=`#009246`, Grecia=`#0D5EAF`  
- **Título:** "Revenue por país"

### Franja 4 — Distribución

#### Donut — Mix de canales (25 % del ancho)
- **Tipo:** Donut chart  
- **Leyenda:** `dim_channel[channel]`  
- **Valores:** `[Revenue Neto]`  
- **Etiquetas de detalle:** porcentaje + nombre de canal  
- **Título:** "Mix de canales"

#### Mapa geográfico (40 % del ancho)
- **Tipo:** Map o Azure Maps  
- **Ubicación:** `dim_hotel[country]` *(asegurarse de que Data category = Country)*  
- **Tamaño de burbuja:** `[Revenue Neto]`  
- **Tooltip:** `[Revenue Neto]`, `[Reservas Totales]`, `[Cancellation Rate]`  
- **Título:** "Distribución geográfica"

#### Top 10 hoteles (35 % del ancho)
- **Tipo:** Bar chart (horizontal)  
- **Eje Y:** `dim_hotel[hotel_name]`  
- **Valores:** `[Revenue Neto]`  
- **Filtro visual (Filters on this visual):** `[Ranking Hotel por Revenue]` es menor o igual que `10`  
- **Ordenar:** descendente por Revenue Neto  
- **Título:** "Top 10 hoteles por revenue"

---

## Página 2 — Análisis Temporal

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  SLICER Año (multi) │ SLICER País                                │
├────────────┬────────────┬──────────────────────────────────────┤
│ Revenue YTD│Revenue QTD │ Revenue MoM %                         │  ← KPI cards
├────────────┴────────────┴──────────────────────────────────────┤
│                                                                  │
│         Área: Evolución mensual Revenue vs. Año Anterior         │  ← gráfico principal
│                                                                  │
├─────────────────────────────┬────────────────────────────────────┤
│  Columnas: Estacionalidad   │  Barras: Por temporada             │
│  por mes (agrupado por año) │                                    │
├─────────────────────────────┴────────────────────────────────────┤
│    Matrix: Detalle mensual Revenue, ADR y Reservas YoY           │
└──────────────────────────────────────────────────────────────────┘
```

### Slicers
| Visual | Campo | Tipo |
|---|---|---|
| Año | `Calendario[Año]` | Slicer lista, multi-select |
| País | `dim_hotel[country]` | Slicer lista, multi-select |

### KPI Cards (3)
| Tarjeta | Medida | Formato |
|---|---|---|
| Revenue YTD | `[Revenue YTD]` | `€ #,##0` |
| Revenue QTD | `[Revenue QTD]` | `€ #,##0` |
| Revenue MoM % | `[Revenue MoM %]` | `+0.0%;-0.0%;0.0%` · flecha verde/roja |

### Gráfico principal — Área (ancho completo)
- **Tipo:** Area chart  
- **Eje X:** `Calendario[Año Mes]`  
- **Valores área:** `[Revenue Neto]` — color `#0053A0` con 20 % de opacidad  
- **Valores línea:** `[Revenue Año Anterior]` — color `#9CA3AF`, línea  
- **Tooltip:** `[Revenue YoY %]`, `[Reservas Totales]`  
- **Título:** "Evolución mensual del Revenue"

### Estacionalidad por mes
- **Tipo:** Clustered column chart  
- **Eje X:** `Calendario[Mes Nombre Corto]` *(ordenar por `Mes`)*  
- **Valores:** `[Revenue Neto]`  
- **Leyenda:** `Calendario[Año]`  
- **Título:** "Estacionalidad por mes"

### Por temporada
- **Tipo:** Clustered bar chart  
- **Eje Y:** `Calendario[Temporada]`  
- **Valores:** `[Revenue Neto]`, `[ADR]`  
- **Título:** "Rendimiento por temporada"

### Matrix — Detalle mensual (ancho completo)
- **Filas:** `Calendario[Año]` → `Calendario[Mes Nombre Corto]`  
- **Valores:**

| Columna | Medida | Formato |
|---|---|---|
| Revenue Neto | `[Revenue Neto]` | `€ #,##0` |
| vs. Año Ant. | `[Revenue Año Anterior]` | `€ #,##0` |
| YoY % | `[Revenue YoY %]` | `+0.0%;-0.0%` · escala verde→rojo |
| ADR | `[ADR]` | `€ #,##0.00` |
| ADR YoY % | `[ADR YoY %]` | `+0.0%;-0.0%` · escala |
| Reservas | `[Reservas Totales]` | `#,##0` |

- **Subtotales:** activar solo por año  
- **Formato condicional en YoY %:** reglas — valor > 0 fondo `#D1FAE5`, valor < 0 fondo `#FEE2E2`

---

## Página 3 — Rendimiento de Hoteles

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  SLICER Año │ SLICER País (multi) │ SLICER Temporada             │
├───────────┬───────────┬──────────────────┬────────────────────────┤
│  Hoteles  │    ADR    │  Lead Time Prom  │  Revenue por Plaza     │  ← KPIs
│  Activos  │           │                  │                        │
├───────────┴───────────┴──────────────────┴────────────────────────┤
│                                                                    │
│              Barras horizontales: Revenue por hotel                │  ← ranking
│                                                                    │
├──────────────────────────────┬─────────────────────────────────────┤
│  Scatter: ADR vs Revenue     │  Tabla: Ranking completo            │
│  (tamaño = noches vendidas)  │                                     │
├──────────────────────────────┴─────────────────────────────────────┤
│         Columnas agrupadas: Revenue y ADR por ciudad               │
└────────────────────────────────────────────────────────────────────┘
```

### Slicers
| Visual | Campo | Tipo |
|---|---|---|
| Año | `Calendario[Año]` | Dropdown |
| País | `dim_hotel[country]` | Lista, multi-select |
| Temporada | `Calendario[Temporada]` | Lista, multi-select |

### KPI Cards (4)
| Tarjeta | Medida | Formato |
|---|---|---|
| Hoteles Activos | `[Hoteles Activos]` | `#,##0` |
| ADR | `[ADR]` | `€ #,##0.00` |
| Lead Time Promedio | `[Lead Time Promedio]` | `#,##0` " días" |
| Revenue por Plaza | `[Revenue por Plaza Adulto]` | `€ #,##0.00` |

### Ranking principal — Barras por hotel (ancho completo)
- **Tipo:** Bar chart (horizontal)  
- **Eje Y:** `dim_hotel[hotel_name]`  
- **Valores:** `[Revenue Neto]`  
- **Leyenda (color):** `dim_hotel[country]` — España=`#0053A0`, Italia=`#009246`, Grecia=`#0D5EAF`  
- **Etiquetas de datos:** activadas  
- **Ordenar:** descendente por Revenue Neto  
- **Título:** "Revenue Neto por hotel"

### Scatter — ADR vs Revenue (50 % ancho)
- **Tipo:** Scatter chart  
- **Eje X:** `[ADR]` — *"¿Es caro?"*  
- **Eje Y:** `[Revenue Neto]` — *"¿Genera negocio?"*  
- **Detalles (puntos):** `dim_hotel[hotel_name]`  
- **Tamaño:** `[Noches Vendidas]`  
- **Color:** `dim_hotel[country]`  
- **Título:** "ADR vs Revenue · tamaño = noches vendidas"  
- **Cuadrante de referencia** *(líneas de referencia)*: añadir línea horizontal y vertical en el valor promedio de ADR y Revenue respectivamente (Reference lines → Average)

### Tabla ranking completo (50 % ancho)
- **Tipo:** Table  
- **Columnas:**

| Campo | Medida | Formato | Condicional |
|---|---|---|---|
| `dim_hotel[hotel_name]` | — | Texto | — |
| `dim_hotel[country]` | — | Texto | — |
| `[Revenue Neto]` | — | `€ #,##0` | Barras de datos |
| `[ADR]` | — | `€ #,##0.00` | — |
| `[Cancellation Rate]` | — | `0.0%` | Semáforo |
| `[Ranking Hotel por Revenue]` | — | `#,##0` | — |

- **Ordenar:** por Ranking Hotel por Revenue ascendente

### Columnas por ciudad (ancho completo)
- **Tipo:** Clustered column chart  
- **Eje X:** `dim_hotel[city]`  
- **Valores:** `[Revenue Neto]` (eje Y izquierdo), `[ADR]` (eje Y derecho)  
- **Eje Y secundario:** activar para ADR  
- **Título:** "Revenue y ADR por ciudad"

---

## Página 4 — Análisis de Cancelaciones

### Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  SLICER Año │ SLICER País │ SLICER Canal                         │
├──────────┬──────────┬──────────────────┬──────────────────────────┤
│Canceladas│Cancel.   │  Lead Time Prom  │  Lead Time Máx           │  ← KPIs
│          │  Rate    │                  │                          │
├──────────┴──────────┴──────────────────┴──────────────────────────┤
│  Línea+Columna:                │  Barras: Cancelaciones           │
│  Cancelaciones mensuales       │  por canal                       │
│  + Tasa sobre eje secundario   │                                  │
├────────────────────────────────┴──────────────────────────────────┤
│  Columnas: Distribución        │  Matrix: Cancellation Rate       │
│  por tramo de lead time        │  por país y temporada            │
├────────────────────────────────┴──────────────────────────────────┤
│      Tabla: Hoteles con mayor tasa de cancelación                  │
└────────────────────────────────────────────────────────────────────┘
```

### Slicers
| Visual | Campo | Tipo |
|---|---|---|
| Año | `Calendario[Año]` | Dropdown |
| País | `dim_hotel[country]` | Lista, multi-select |
| Canal | `dim_channel[channel]` | Lista, multi-select |

### KPI Cards (4)
| Tarjeta | Medida | Formato |
|---|---|---|
| Reservas Canceladas | `[Reservas Canceladas]` | `#,##0` |
| Cancellation Rate | `[Cancellation Rate]` | `0.0%` · semáforo |
| Lead Time Promedio | `[Lead Time Promedio]` | `#,##0` " días" |
| Lead Time Máximo | `[Lead Time Máximo]` | `#,##0` " días" |

### Gráfico izquierdo — Cancelaciones mensuales (55 % ancho)
- **Tipo:** Line and Clustered Column chart  
- **Eje X:** `Calendario[Mes Nombre Corto]`  
- **Columnas:** `[Reservas Canceladas]` — color `#E63946`  
- **Línea (eje secundario):** `[Cancellation Rate]` — color `#F59E0B`  
- **Título:** "Cancelaciones y tasa mensual"

### Gráfico derecho — Por canal (45 % ancho)
- **Tipo:** Bar chart horizontal  
- **Eje Y:** `dim_channel[channel]`  
- **Valores:** `[Reservas Canceladas]`, `[Cancellation Rate]`  
- **Título:** "Cancelaciones por canal de reserva"

### Gráfico izquierdo — Tramos de lead time (50 % ancho)
- **Tipo:** Column chart  
- **Eje X:** `reservas[Tramo Lead Time]` *(columna calculada, ver inicio del documento)*  
- **Valores:** `[Reservas Canceladas]`  
- **Color:** `#E63946`  
- **Título:** "Cancelaciones por antelación de reserva"  
- **Insight esperado:** si el mayor bloque está en "0-7 días", el problema es cancelaciones de último minuto; si está en ">180 días", el problema son reservas anticipadas que luego se cancelan.

### Matrix — Cancellation Rate por país y temporada (50 % ancho)
- **Tipo:** Matrix  
- **Filas:** `dim_hotel[country]`  
- **Columnas:** `Calendario[Temporada]`  
- **Valores:** `[Cancellation Rate]`  
- **Formato condicional:** escala de color — mínimo `#D1FAE5` (verde), máximo `#FEE2E2` (rojo)  
- **Título:** "Cancellation Rate por país y temporada"

### Tabla — Hoteles con mayor cancelación (ancho completo)
- **Tipo:** Table  
- **Columnas:**

| Campo/Medida | Formato | Condicional |
|---|---|---|
| `dim_hotel[hotel_name]` | Texto | — |
| `dim_hotel[country]` | Texto | — |
| `[Reservas Totales]` | `#,##0` | — |
| `[Reservas Canceladas]` | `#,##0` | Barras de datos color `#E63946` |
| `[Cancellation Rate]` | `0.0%` | Semáforo |
| `[Ranking Hotel Menor Cancelación]` | `#,##0` | — |

- **Filtro visual:** mostrar solo los 15 hoteles con mayor `[Reservas Canceladas]`  
- **Ordenar:** por Reservas Canceladas descendente  
- **Título:** "Hoteles con mayor tasa de cancelación"

---

## Slicers sincronizados entre páginas

En **View → Sync slicers**, configurar:

| Slicer | Páginas donde sincronizar | Páginas donde mostrar |
|---|---|---|
| Año | 1, 2, 3, 4 | 1, 2, 3, 4 |
| País | 1, 2, 3, 4 | 1, 2, 3, 4 |
| Canal | 1, 4 | 1, 4 |
| Temporada | 1, 3 | 1, 3 |

---

## Interacciones entre visuals

En **Format → Edit interactions**, configurar en cada página:

**Página 1:** el gráfico de barras por país filtra el mapa y el Top 10 hoteles. El donut de canales filtra solo las líneas temporales.

**Página 3:** el scatter ADR vs Revenue y la tabla de ranking deben interactuar bidireccionalmente — al seleccionar un hotel en el scatter se resalta en la tabla y viceversa.

**Página 4:** el gráfico de tramos de lead time **no filtra** la tabla de hoteles (establecer interacción en "none") para que la tabla siempre muestre el top 15 independientemente de la selección de tramo.

---

## Tooltips personalizados (opcional, nivel avanzado)

Crear una **página de tooltip** (Page information → Allow use as tooltip):

**Tooltip: Detalle de hotel**
- `dim_hotel[hotel_name]` (título)
- `[Revenue Neto]`, `[ADR]`, `[Cancellation Rate]`, `[Lead Time Promedio]`, `[Ranking Hotel por Revenue]`
- Tamaño de página: 320 × 240 px

Asignar este tooltip a los visuals de la Página 3 que tienen `dim_hotel[hotel_name]` como detalle.

---

## Checklist de implementación

### Modelo
- [ ] Medida `RevPAR` creada en carpeta `01 - KPIs Base`
- [ ] Medida `Reservas YTD` creada en carpeta `03 - Time Intelligence`
- [ ] Medida `Hoteles Activos` creada en carpeta `02 - Análisis`
- [ ] Columna calculada `Tramo Lead Time` creada en tabla `reservas`
- [ ] Columnas FK/PK ocultas (`booking_id`, `customer_id`, `hotel_id`, `channel_id`, etc.)
- [ ] Categorías geográficas asignadas (`country` → Country, `city` → City)
- [ ] `Calendario` marcada como Date Table (`Mark as date table → Date`)

### Dashboard
- [ ] Página 1 — Vista Ejecutiva completa (5 cards, 2 gráficos grandes, 3 gráficos pequeños)
- [ ] Página 2 — Análisis Temporal completa (3 cards, área, 2 gráficos, matrix)
- [ ] Página 3 — Rendimiento de Hoteles completa (4 cards, ranking, scatter, tabla, ciudades)
- [ ] Página 4 — Cancelaciones completa (4 cards, línea+col, canal, lead time, matrix, tabla)
- [ ] Slicers sincronizados entre páginas
- [ ] Interacciones entre visuals configuradas
- [ ] Paleta de colores aplicada (tema o configuración manual)
- [ ] Fondo de página `#F4F6F9` aplicado en las 4 páginas
- [ ] Títulos de página añadidos como cuadros de texto en la parte superior

### Archivo final
- [ ] Guardado como `HotelesMediterraneum_7.5.2_resuelto_FINAL.pbix`

---

*Guía de implementación del cuadro de mando · HotelesMediterraneum · Bloque 7 Power BI*
