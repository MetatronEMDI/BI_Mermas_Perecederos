import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# Recuperar los resultados del pronóstico
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

df = pd.read_csv(
    DATA_DIR / "pronostico_dairy_tienda3.csv",
    parse_dates=["date"]
).sort_values("date")

app = Dash(__name__)
app.title = "BI | Riesgo de Merma"

# Gráfica histórica: ventas observadas contra pronóstico
fig_ventas = go.Figure()

fig_ventas.add_scatter(
    x=df["date"], y=df["ventas_reales"],
    name="Ventas reales", mode="lines+markers"
)

fig_ventas.add_scatter(
    x=df["date"], y=df["pronostico"],
    name="Pronóstico", mode="lines"
)

fig_ventas.update_layout(
    title="Ventas reales vs. pronóstico",
    template="plotly_white",
    xaxis_title="Fecha",
    yaxis_title="Volumen vendido"
)

# Recuperar clasificación ABC
abc = pd.read_csv(DATA_DIR / "abc_productos.csv")
abc = abc.sort_values("ventas", ascending=False).reset_index(drop=True)

# Construir diagrama de Pareto
fig_pareto = go.Figure()

fig_pareto.add_bar(
    x=abc.index + 1,
    y=abc["ventas"],
    name="Volumen vendido"
)

fig_pareto.add_scatter(
    x=abc.index + 1,
    y=abc["acumulado_pct"],
    name="Participación acumulada",
    mode="lines",
    yaxis="y2"
)

fig_pareto.update_layout(
    title="Análisis ABC - Productos perecederos",
    template="plotly_white",
    xaxis_title="Ranking de productos",
    yaxis_title="Volumen vendido",
    yaxis2=dict(
        title="Participación acumulada (%)",
        overlaying="y",
        side="right",
        range=[0, 105]
    )
)

fig_pareto.update_xaxes(rangeslider_visible=True)

# Diseño de las tarjetas de indicadores
def tarjeta(titulo, identificador):
    return html.Div([
        html.P(titulo, style={
            "color": "#64748b",
            "fontSize": "14px",
            "marginBottom": "8px"
        }),
        html.H2(id=identificador, style={
            "color": "#0f172a",
            "fontSize": "28px",
            "margin": "0"
        })
    ], style={
        "backgroundColor": "white",
        "padding": "22px",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.06)",
        "border": "1px solid #e2e8f0",
        "flex": "1",
        "minWidth": "190px"
    })

# Interfaz del dashboard
app.layout = html.Div([

    html.H1("Inteligencia de Negocios | Riesgo de Merma"),
    html.P("Producto DAIRY 1427659 | Tienda 3 | Escenario simulado"),

    html.Div([
        tarjeta("Demanda prevista", "kpi-demanda"),
        tarjeta("Unidades en riesgo", "kpi-unidades"),
        tarjeta("Tasa de riesgo", "kpi-tasa"),
        tarjeta("Valor económico expuesto", "kpi-valor")
    ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),

    html.H3("Simulador de inventario"),

    html.Label("Inventario disponible (unidades)"),
    dcc.Slider(
        min=0, max=1500, step=50, value=900,
        id="inventario",
        marks={i: str(i) for i in range(0, 1501, 250)}
    ),

    html.Label("Vida útil restante (días)"),
    dcc.Slider(
        min=1, max=15, step=1, value=5,
        id="vida-util",
        marks={i: str(i) for i in range(1, 16, 2)}
    ),

    html.Label("Costo unitario (MXN)"),
    dcc.Input(
        id="costo", type="number",
        value=30, min=0, step=1
    ),

    html.Div([
        dcc.Graph(
            figure=fig_ventas,
            style={"flex": "1", "minWidth": "350px"}
        ),
        dcc.Graph(
            id="grafica-riesgo",
            style={"flex": "1", "minWidth": "350px"}
        )
    ], style={"display": "flex", "flexWrap": "wrap"}),

    html.H3("Análisis de concentración comercial"),
    dcc.Graph(figure=fig_pareto),

    html.H3("Inteligencia para la toma de decisiones"),

    html.Div(
        id="recomendacion",
        style={
            "backgroundColor": "white",
            "padding": "24px",
            "borderRadius": "12px",
            "borderLeft": "5px solid #168777",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.06)"
        }
    ),

    html.H3("Exportación de resultados"),

    html.P(
        "Descarga los indicadores del escenario actual "
        "para su interpretación mediante IA generativa"
    ),

    html.Button(
        "Descargar informe para IA (PDF)",
        id="btn-pdf",
        n_clicks=0,
        style={
            "backgroundColor": "#168777",
            "color": "white",
            "padding": "12px 24px",
            "border": "none",
            "borderRadius": "8px",
            "cursor": "pointer",
            "fontSize": "15px"
        }
    ),
    dcc.Download(id="descarga-pdf"),

    html.P(
        "Nota: inventario, caducidad y costos son simulados. "
        "Las cifras representan exposición potencial, no pérdidas reales.",
        style={"color": "#64748b"}
    )

], style={
    "fontFamily": "Segoe UI, Arial, sans-serif",
    "backgroundColor": "#f4f7fb",
    "padding": "32px",
    "minHeight": "100vh",
    "color": "#0f172a"
})

@app.callback(
    Output("descarga-pdf", "data"),
    Input("btn-pdf", "n_clicks"),
    State("inventario", "value"),
    State("vida-util", "value"),
    State("costo", "value"),
    prevent_initial_call=True
)

def descargar_pdf(n_clicks, inventario, vida_util, costo):
    #Recuperar los parámetros actuales
    inventario = inventario or 0
    costo = max(0, float(costo or 0))

    #Recalcular los indicadores del escenario
    demanda = df["pronostico"].head(vida_util).sum()
    excedente = max(0, inventario - demanda)
    faltante = max(0, demanda - inventario)
    tasa = excedente / inventario * 100 if inventario > 0 else 0
    valor = excedente * costo

    # Crear PDF en memoria
    buffer = BytesIO()
    documento = SimpleDocTemplate(buffer)
    estilos = getSampleStyleSheet()

    contenido = [
        Paragraph("INFORME DE INTELIGENCIA DE NEGOCIOS", estilos["Title"]),
        Spacer(1, 16),

        Paragraph("Producto: DAIRY 1427659 | Tienda: 3", estilos["Normal"]),
        Paragraph("Periodo de referencia: julio-agosto de 2017", estilos["Normal"]),
        Spacer(1, 16),

        Paragraph("Indicadores del pronostico", estilos["Heading2"]),
        Paragraph("Método: promedio de los últimos 28 días", estilos["Normal"]),
        Paragraph("MAE: 18.34 unidades diarias", estilos["Normal"]),
        Paragraph("WAPE: 13.04% (31 días evaluados)", estilos["Normal"]),
        Spacer(1, 12),

               Paragraph("Escenario de inventario simulado", estilos["Heading2"]),
        Paragraph(f"Inventario inicial: {inventario:,.2f}", estilos["Normal"]),
        Paragraph(f"Vida util restante: {vida_util} dias", estilos["Normal"]),
        Paragraph(f"Costo unitario: ${costo:,.2f} MXN", estilos["Normal"]),
        Paragraph(f"Demanda prevista: {demanda:,.2f}", estilos["Normal"]),
        Paragraph(f"Excedente potencial: {excedente:,.2f}", estilos["Normal"]),
        Paragraph(f"Faltante potencial: {faltante:,.2f}", estilos["Normal"]),
        Paragraph(f"Tasa de inventario en riesgo: {tasa:.2f}%", estilos["Normal"]),
        Paragraph(f"Valor economico expuesto: ${valor:,.2f} MXN", estilos["Normal"]),
        Spacer(1, 12),

        Paragraph("Contexto comercial", estilos["Heading2"]),
        Paragraph(
            "869 productos perecederos analizados. "
            "La categoria A comprende 414 productos y "
            "concentra el 80.03% del volumen positivo vendido.",
            estilos["Normal"]
        ),
        Spacer(1, 12),

        Paragraph("Limitaciones", estilos["Heading2"]),
        Paragraph(
            "Las ventas historicas proceden de datos reales. "
            "El inventario, la vida util y el costo son simulados. "
            "El excedente es una estimacion basada en un pronostico "
            "puntual, no una merma observada. "
            "No se ha demostrado una reduccion efectiva de perdidas.",
            estilos["Normal"]
        )
    ]

    documento.build(contenido)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return dcc.send_bytes(pdf_bytes, "informe_bi_mermas.pdf")      

# Recalcular los indicadores al modificar los controles
@app.callback(
    Output("kpi-demanda", "children"),
    Output("kpi-unidades", "children"),
    Output("kpi-tasa", "children"),
    Output("kpi-valor", "children"),
    Output("grafica-riesgo", "figure"),
    Output("recomendacion", "children"),
    Input("inventario", "value"),
    Input("vida-util", "value"),
    Input("costo", "value")
)

def actualizar(inventario, vida_util, costo):

    costo = max(0, float(costo or 0))

    demanda = df["pronostico"].head(vida_util).sum()
    excedente = max(0, inventario - demanda)
    cobertura = min(inventario, demanda)

    tasa = excedente / inventario * 100 if inventario > 0 else 0
    valor = excedente * costo

    # Evaluar el escenario comercial
    faltante = max(0, demanda - inventario)

    if excedente > 0:
        diagnostico = (
            f"Se estima un excedente potencial de {excedente:.2f} "
            f"unidades, equivalente al {tasa:.2f}% del inventario."
        )

        accion = (
            "Priorizar la salida del lote próximo a caducar y "
            "revisar las cantidades de reposición. Evaluar promociones "
            "únicamente si el margen comercial lo permite."
        )

    elif faltante > 0:
        diagnostico = (
            f"El inventario es inferior a la demanda prevista "
            f"en {faltante:.2f} unidades."
        )

        accion = (
            "Revisar la disponibilidad y evaluar una reposición "
            "para reducir el riesgo de desabasto."
        )

    else:
        diagnostico = (
            "El inventario coincide con la demanda acumulada "
            "prevista durante la vida útil restante."
        )

        accion = (
            "Mantener el seguimiento de las ventas y revisar "
            "el pronóstico antes de nuevas reposiciones."
        )
    
    # Construir el informe empresarial
    informe = html.Div([
        html.H4("Diagnóstico comercial"),
        html.P(diagnostico),

        html.H4("Acción recomendada"),
        html.P(accion),

        html.Small(
            "Recomendación basada en reglas y supuestos simulados. "
            "No representa una pérdida observada ni garantiza "
            "la eliminación de mermas.",
            style={"color": "#64748b"}
        )
    ])

    fig = go.Figure()

    fig.add_bar(
        y=["Inventario"],
        x=[cobertura],
        orientation="h",
        name="Venta prevista cubierta",
        marker_color="#168777"
    )

    fig.add_bar(
        y=["Inventario"],
        x=[excedente],
        orientation="h",
        name="Inventario en riesgo",
        marker_color="#e5a446"
    )

    fig.update_layout(
        title="Composición del inventario",
        barmode="stack",
        template="plotly_white",
        xaxis_title="Unidades",
        height=350
    )

    return (
        f"{demanda:,.2f}",
        f"{excedente:,.2f}",
        f"{tasa:.2f}%",
        f"${valor:,.2f} MXN",
        fig,
        informe
    )

if __name__ == "__main__":
    app.run(debug=False)
