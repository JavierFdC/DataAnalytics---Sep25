"""
Mercadia · Segmentación RFM de clientes
Bloque 9 - Qlik · Sesión 9.1.4

Lee las ventas y los clientes de Mercadia, aplica las mismas reglas de limpieza
que el script de carga de Qlik (sesión 9.1.2), calcula la Recencia, la Frecuencia
y el valor Monetario de cada cliente y exporta segmentos_rfm.csv para cargarlo
en la app de Qlik.

Uso (desde la carpeta "9. Qlik"):
    python "9.1 - Fundamentos/9.1.4 - segmentacion_rfm.py"
"""

from pathlib import Path

import pandas as pd

RUTA_DATASET = Path(__file__).resolve().parent.parent / "9.0 - Dataset"
FECHA_CORTE = pd.Timestamp("2026-09-30")  # último día con datos en la muestra

ORDEN_SEGMENTOS = [
    "Campeones",
    "Leales",
    "Nuevos",
    "Necesitan atención",
    "En riesgo",
    "Perdidos",
    "Sin compras",
]


def leer_ventas(ruta: Path) -> pd.DataFrame:
    """Carga ventas_mercadia.csv con las reglas de limpieza de la 9.1.2."""
    ventas = pd.read_csv(ruta, dtype={"id_cliente": "string"})

    # Tres formatos de fecha: se prueba cada uno y se combinan (como Alt + Date# en Qlik)
    texto = ventas["fecha"]
    fecha = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
    fecha = fecha.fillna(pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce"))
    fecha = fecha.fillna(pd.to_datetime(texto, format="%d-%m-%y", errors="coerce"))
    ventas["fecha"] = fecha

    # Líneas imposibles: 0 unidades (WHERE unidades <> 0)
    ventas = ventas[ventas["unidades"] != 0].copy()

    # Importes con la coma decimal perdida: se recalculan (preceding load de la 9.1.2)
    calculado = (
        ventas["unidades"] * ventas["precio_unitario"] * (1 - ventas["descuento_pct"])
    ).round(2)
    erroneo = (ventas["importe_neto"] - calculado).abs() > 0.05
    ventas.loc[erroneo, "importe_neto"] = calculado[erroneo]

    # Solo las ventas con tarjeta de cliente
    ventas["id_cliente"] = ventas["id_cliente"].fillna("").str.strip()
    return ventas[ventas["id_cliente"] != ""]


def asignar_segmento(fila: pd.Series) -> str:
    """Reglas de segmentación a partir de las puntuaciones de Recencia y Frecuencia."""
    r, f = fila["r_score"], fila["f_score"]
    if r >= 4 and f >= 4:
        return "Campeones"
    if r >= 3 and f >= 3:
        return "Leales"
    if r >= 4:
        return "Nuevos"
    if r <= 2 and f >= 3:
        return "En riesgo"
    if r <= 2:
        return "Perdidos"
    return "Necesitan atención"


def calcular_rfm(ventas: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cliente con sus métricas RFM, puntuaciones 1-5 y segmento."""
    rfm = ventas.groupby("id_cliente").agg(
        ultima_compra=("fecha", "max"),
        rfm_frecuencia=("id_ticket", "nunique"),
        rfm_valor=("importe_neto", "sum"),
    )
    rfm["rfm_recencia_dias"] = (FECHA_CORTE - rfm["ultima_compra"]).dt.days
    rfm["rfm_valor"] = rfm["rfm_valor"].round(2)

    # Quintiles: cada puntuación agrupa al 20 % de los clientes.
    # rank(method="first") deshace los empates (hay cientos de clientes con 1 o 2 tickets).
    # En la recencia, menos días es mejor: la puntuación va al revés.
    rfm["r_score"] = pd.qcut(
        rfm["rfm_recencia_dias"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
    ).astype(int)
    rfm["f_score"] = pd.qcut(
        rfm["rfm_frecuencia"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
    rfm["m_score"] = pd.qcut(
        rfm["rfm_valor"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["segmento_rfm"] = rfm.apply(asignar_segmento, axis=1)
    return rfm.drop(columns="ultima_compra").reset_index()


def main() -> None:
    ventas = leer_ventas(RUTA_DATASET / "ventas_mercadia.csv")
    rfm = calcular_rfm(ventas)

    # Todos los clientes del maestro, también los que nunca han comprado
    clientes = pd.read_csv(
        RUTA_DATASET / "clientes.csv", usecols=["id_cliente"], dtype={"id_cliente": "string"}
    )
    clientes = clientes.drop_duplicates()
    segmentos = clientes.merge(rfm, on="id_cliente", how="left")
    segmentos["segmento_rfm"] = segmentos["segmento_rfm"].fillna("Sin compras")

    columnas = [
        "id_cliente",
        "segmento_rfm",
        "rfm_recencia_dias",
        "rfm_frecuencia",
        "rfm_valor",
        "r_score",
        "f_score",
        "m_score",
    ]
    for col in ["rfm_recencia_dias", "rfm_frecuencia", "r_score", "f_score", "m_score"]:
        segmentos[col] = segmentos[col].astype("Int64")  # enteros que admiten nulos

    salida = RUTA_DATASET / "segmentos_rfm.csv"
    segmentos[columnas].to_csv(salida, index=False, encoding="utf-8")

    resumen = (
        segmentos.groupby("segmento_rfm")
        .agg(clientes=("id_cliente", "count"), ventas=("rfm_valor", "sum"))
        .reindex(ORDEN_SEGMENTOS)
    )
    print(f"Clientes con compras: {len(rfm):,}".replace(",", "."))
    print(resumen.to_string())
    print(f"\nArchivo generado: {salida}")


if __name__ == "__main__":
    main()
