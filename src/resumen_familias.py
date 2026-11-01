# Realizar el Análisis de Participación Comercial (sales mix) basado en volúmen

import pandas as pd 
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

resumen = None

# Lectura por bloques del archivo de ventas de perecederos
for bloque in pd.read_csv(
    DATA_DIR / "ventas_perecederos.csv",
    chunksize=250000,
    usecols=["family", "unit_sales"]
):

    bloque["positivas"] = bloque["unit_sales"].clip(lower=0)
    bloque["negativas"] = bloque["unit_sales"].clip(upper=0).abs()

    # Agrupar los resultados por familia

    parcial = bloque.groupby("family").agg(
        registros=("unit_sales", "size"),
        unidades_positivas=("positivas", "sum"),
        unidades_negativas=("negativas", "sum")
    )

    # Acumular resultados de todos los bloques
    resumen = parcial if resumen is None else resumen.add(parcial, fill_value=0)

# Calcular el volumen neto
resumen["volumen_neto"] = (
    resumen["unidades_positivas"] - resumen["unidades_negativas"]
)

# Calcular la participación relativa
resumen["participacion_pct"] = (
    resumen["unidades_positivas"] / 
    resumen["unidades_positivas"].sum() * 100
)

# Ordenar familiar según volumen positivo
resumen = resumen.sort_values("unidades_positivas", ascending=False)

# Mostrar y guardar resultados
print("\nRESUMEN DE PARTICIPACIÓN COMERCIAL:")
print(resumen.round(2).to_string())

resumen.to_csv(DATA_DIR / "resumen_familias.csv")
    