import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Ubicación de los datos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Producto, tienda y periodo seleccionados
PRODUCTO = 1427659
TIENDA = 3
INICIO = "2016-08-16"
FIN = "2017-07-15"

registros = []

# Leer y filtrar las ventas por bloques
for bloque in pd.read_csv(
    DATA_DIR / "ventas_perecederos.csv",
    usecols=["date", "store_nbr", "item_nbr", "unit_sales"],
    chunksize=250000
):
    filtrado = bloque[
        (bloque["store_nbr"] == TIENDA) &
        (bloque["item_nbr"] == PRODUCTO) &
        (bloque["date"] >= INICIO) &
        (bloque["date"] <= FIN)
    ]

    if not filtrado.empty:
        registros.append(filtrado)

# Unificar registros y convertir fechas
df = pd.concat(registros, ignore_index=True)
df["date"] = pd.to_datetime(df["date"])

# Calcular ventas positivas registradas por día
df["ventas"] = df["unit_sales"].clip(lower=0)

serie = df.groupby("date")["ventas"].sum()

# Creación de calendario diario sin inventar ventas faltantes
calendario = pd.date_range(INICIO, FIN, freq="D")
serie = serie.reindex(calendario)

# Crear tabla y calcular media móvil de 7 días
serie = serie.rename("ventas").to_frame()
serie.index.name = "date"

serie["media_7d"] = serie["ventas"].rolling(
    window=7, min_periods=5
).mean()

# Verificar registros y días sin información
print("Registros originales:", len(df))
print("Días con información:", serie["ventas"].count())
print("Días sin información:", serie["ventas"].isna().sum())
print("Fechas duplicadas:", df.duplicated(subset=["date"]).sum())

# Guardar la serie para el modelo predictivo
serie.to_csv(DATA_DIR / "serie_dairy_tienda3.csv")

# Visualización con plotly
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=serie.index,
    y=serie["ventas"],
    mode="lines",
    name="Ventas diarias" 
))

fig.add_trace(go.Scatter(
    x=serie.index,
    y=serie["media_7d"],
    mode="lines",
    name="Media móvil de 7 días",
    line=dict(width=3)
))

fig.update_layout(
    title="Evolución diaria de ventas - Dairy",
    xaxis_title="Fecha",
    yaxis_title="Volumen positivo registrado",
    template="plotly_white",
    hovermode="x unified"
)

fig.show(renderer="browser")