from matplotlib import use
import pandas as pd
from pathlib import Path

# Directorio de datos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

resumen = None

# Procesar las ventas por bloques
for bloque in pd.read_csv(
    DATA_DIR / "ventas_perecederos.csv",
    usecols=["date", "store_nbr", "item_nbr", "unit_sales", "family"],
    chunksize=250000
):

    # Seleccionar lácteor del periodo de desarrollo
    dairy = bloque[
        (bloque["family"] == "DAIRY") &
        (bloque["date"] >= "2016-08-16") &
        (bloque["date"] <= "2017-07-15")
    ].copy()

    # Calcular ventas positivas
    dairy["ventas"] = dairy["unit_sales"].clip(lower=0)

    # Agrupar por establecimiento y producto
    parcial = dairy.groupby(["store_nbr", "item_nbr"]).agg(
        registros=("date", "size"),
        volumen=("ventas", "sum")
    )

    # Acumular resultados
    resumen = parcial if resumen is None else resumen.add(parcial, fill_value=0)

# Seleccionar productos con suficientes registros
candidatos = resumen[resumen["registros"] >= 270]

# Ordenar por volumen vendido
candidatos = candidatos.sort_values("volumen", ascending=False)

print("\nTOP 10 CANDIDATOS PARA PREDICCIÓN")
print(candidatos.head(10).to_string())

print("\n Total de combinaciones elegibles:", len(candidatos))


