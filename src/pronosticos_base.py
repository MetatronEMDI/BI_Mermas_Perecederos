import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Leer la serie de desarrollo
train = pd.read_csv(
    DATA_DIR / "serie_dairy_tienda3.csv",
    parse_dates=["date"]
)

# Identificar los cinco días sin registro
print("Fechas faltantes:")
print(train.loc[train["ventas"].isna(), "date"].dt.strftime("%Y-%m-%d").tolist())

# Calcular el promedio histórico por día de la semana
train["dia_semana"] = train["date"].dt.dayofweek
perfil = train.groupby("dia_semana")["ventas"].mean()

# Recuperar las ventas reales del preriodo de evaluación
registros = []

for bloque in pd.read_csv(
    DATA_DIR / "ventas_perecederos.csv",
    usecols=["date", "store_nbr", "item_nbr", "unit_sales"],
    chunksize=250000
):
    datos = bloque[
        (bloque["store_nbr"] == 3) &
        (bloque["item_nbr"] == 1427659) &
        (bloque["date"] >= "2017-07-16") &
        (bloque["date"] <= "2017-08-15")
    ]

    if not datos.empty:
        registros.append(datos)

# Construir la serie de evaluación
test = pd.concat(registros, ignore_index=True)
test["date"] = pd.to_datetime(test["date"])
test["ventas"] = test["unit_sales"].clip(lower=0)

test = test.groupby("date")["ventas"].sum()
test = test.reindex(pd.date_range("2017-07-16", "2017-08-15"))

# Pronosticar según el día de la semana
prediccion = pd.Series(test.index.dayofweek, index=test.index).map(perfil)

# Evaluar únicamente las fechas con ventas observadas
validos = test.notna() & prediccion.notna()

# Error Absoluto Medio
mae = (test[validos] - prediccion[validos]).abs().mean()
# Error absoluto total en porcentaje
wape=(
    (test[validos] - prediccion[validos]).abs().sum()
    / test[validos].abs().sum() * 100
)

# Modelo alternativo: promedio de los últimos 28 días
ultimos_28 = train["ventas"].tail(28).mean()

# Pronóstico constante para los 31 días de evaluación
pred_28 = pd.Series(ultimos_28, index=test.index)

# Evaluación del modelo alternativo
mae_28 = (test[validos] - pred_28[validos]).abs().mean()

wape_28 = (
    (test[validos] - pred_28[validos]).abs().sum()
    / test[validos].abs().sum() * 100
)

print("\nMODELO ALTERNATIVO - PROMEDIO 28 DÍAS")
print(f"MAE: {mae_28:.2f}")
print(f"WAPE: {wape_28:.2f}%")

print("\nRESULTADOS DEL MODELO BASE")
print("Días evaluados:", validos.sum())
print(f"MAE: {mae:.2f}")
print(f"WAPE: {wape:.2f}%")

# Comparación gráfica
fig = go.Figure()

fig.add_scatter(
    x=test.index, y=test,
    mode="lines+markers", name="Ventas reales"
)

fig.add_scatter(
    x=test.index, y=prediccion,
    mode="lines+markers", name="Pronóstico base"
)

fig.update_layout(
    title="Demanda real vs pronóstico - Producto 1427659",
    xaxis_title="Fecha",
    yaxis_title="Volumen positivo",
    template="plotly_white",
    hovermode="x unified"
)

fig.show(renderer="browser")

# Guardar resultados del modelo seleccionado
resultado = pd.DataFrame({
    "ventas_reales": test,
    "pronostico": pred_28
})

resultado.index.name = "date"

resultado.to_csv(
    DATA_DIR / "pronostico_dairy_tienda3.csv"
)

print("\nPronóstico guardado correctamente")
