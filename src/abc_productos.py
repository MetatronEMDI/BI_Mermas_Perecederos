import pandas as pd
from pathlib import Path

# Directorio de datos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Acumulador de ventas por producto
ventas = pd.Series(dtype="float64")

# Procesar ventas históricas por bloques
for bloque in pd.read_csv(
    DATA_DIR / "ventas_perecederos.csv",
    usecols=["item_nbr", "unit_sales"],
    chunksize=250000
):

    # Considerar únicamente ventas positivas
    parcial = (
        bloque[bloque["unit_sales"] > 0]
        .groupby("item_nbr")["unit_sales"]
        .sum()
    )

    ventas = ventas.add(parcial, fill_value=0)

# Recuperar catálogo de productos seleccionados
productos = pd.read_csv(DATA_DIR / "items.csv")

familias = [
    "DAIRY", "PRODUCE", "BREAD/BAKERY",
    "MEATS", "POULTRY", "EGGS", "SEAFOOD"
]

abc = productos[productos["family"].isin(familias)][
    ["item_nbr", "family"]
].copy()

# Asociar ventas y ordenar de mayor a menor
abc["ventas"] = abc["item_nbr"].map(ventas).fillna(0)
abc = abc.sort_values("ventas", ascending=False).reset_index(drop=True)

# Participación individual y acumulada
abc["participacion_pct"] = abc["ventas"] / abc["ventas"].sum() * 100
abc["acumulado_pct"] = abc["participacion_pct"].cumsum()

# Clasificación ABC
acumulado_previo = abc["acumulado_pct"] - abc["participacion_pct"]

abc["categoria_abc"] = "C"
abc.loc[acumulado_previo < 95, "categoria_abc"] = "B"
abc.loc[acumulado_previo < 80, "categoria_abc"] = "A"

# Mostrar resumen de la clasificación
print("\nCLASIFICACIÓN ABC")
print(abc.groupby("categoria_abc").agg(
    productos=("item_nbr", "count"),
    participacion_pct=("participacion_pct", "sum")
).round(2))

# Mostrar los diez productos con mayor volumen
print("\nTOP 10 PRODUCTOS")
print(abc.head(10).to_string(index=False))

# Guardar resultados
abc.to_csv(DATA_DIR / "abc_productos.csv", index=False)