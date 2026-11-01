import pandas as pd
import plotly.express as px
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

resumen = pd.read_csv(DATA_DIR / "resumen_familias.csv")

# Gráfica de participación comercial
fig = px.bar(
    resumen,
    x="family",
    y="participacion_pct",
    text="participacion_pct",
    title="Participación Comercial de Productos Perecederos",
    labels={
        "family": "Familia comercial",
        "participacion_pct": "Participacion (%)"
    }
)

# Formato de porcentajes
fig.update_traces(
    texttemplate="%{y:.2f}",
    textposition="outside"
)

# Mostrar visualización interactiva
fig.show(renderer="browser")