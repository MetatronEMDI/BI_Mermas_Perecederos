import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Leer los resultados ABC
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
df = pd.read_csv(DATA_DIR / "abc_productos.csv")

# Ordenar productos por volumen vendido
df = df.sort_values("ventas", ascending=False).reset_index(drop=True)
df["ranking"] = df.index + 1

# Crear gráfica con dos ejes verticales
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras: volumen vendido por producto
fig.add_trace(
    go.Bar(
        x=df["ranking"],
        y=df["ventas"],
        name="Volumen vendido",
        customdata=df[["item_nbr", "family", "categoria_abc"]],
        hovertemplate=(
            "Producto: %{customdata[0]}<br>"
            "Familia: %{customdata[1]}<br>"
            "Categoría: %{customdata[2]}<br>"
            "Volumen: %{y:,.2f}<extra></extra>"
        )
    ),
    secondary_y=False
)

# Línea: participación acumulada
fig.add_trace(
    go.Scatter(
        x=df["ranking"],
        y=df["acumulado_pct"],
        mode="lines",
        name="Participación acumulada"
    ),
    secondary_y=True
)

# Umbrales ABC
for limite in [80, 95]:
    fig.add_trace(
        go.Scatter(
            x=[1, len(df)],
            y=[limite, limite],
            mode="lines",
            line=dict(dash="dash"),
            name=f"Umbral {limite}%"
        ),
        secondary_y=True
    )

# Configuración de la gráfica
fig.update_layout(
    title="Diagrama de Pareto - Productos perecederos",
    template="plotly_white",
    hovermode="closest"
)

fig.update_xaxes(
    title_text="Ranking de productos",
    rangeslider_visible=True
)

fig.update_yaxes(
    title_text="Volumen positivo vendido",
    secondary_y=False
)

fig.update_yaxes(
    title_text="Participación acumulada (%)",
    range=[0, 105],
    secondary_y=True
)

# Visualizar en el navegador
fig.show(renderer="browser")