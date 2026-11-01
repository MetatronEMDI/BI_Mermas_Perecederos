import pandas as pd
from pathlib import Path

# Directorio de Datos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Parámetros simulados
INVENTARIO = 900
VIDA_UTIL = 5
COSTO_UNITARIO = 30.0

# Recuperar el pronóstico previamente calculado
df = pd.read_csv(
    DATA_DIR / "pronostico_dairy_tienda3.csv",
    parse_dates=["date"]
)

# Seleccionar los próximos 5 días del escenario
periodo = df.sort_values("date").head(VIDA_UTIL)

# Calcular demanda prevista durante la vida útil
demanda = periodo["pronostico"].sum()

# Estimar inventario protencialmente excedente
excedente = max(0, INVENTARIO - demanda)

# Calcular indicadores económicos
valor_riesgo = excedente * COSTO_UNITARIO
tasa_riesgo = excedente / INVENTARIO * 100

# Mostrar resultados
print("\nESCENARIO SIMULADO DE INVENTARIO")
print(f"Inventario inicial: {INVENTARIO} unidades")
print(f"Demanda prevista: {demanda:.2f}")
print(f"Unidades protencialmente excedentes: {excedente:.2f}")
print(f"Inventario en riesgo: {tasa_riesgo:.2f}%")
print(f"Valor económico expuesto: ${valor_riesgo:,.2f} MXN")

# Guardar indicadores para el dashboard
resultado = pd.DataFrame([{
    "inventario": INVENTARIO,
    "vida_util": VIDA_UTIL,
    "costo_unitario": COSTO_UNITARIO,
    "demanda_prevista": demanda,
    "unidades_riesgo": excedente,
    "tasa_riesgo": tasa_riesgo,
    "valor_riesgo": valor_riesgo
}])

resultado.to_csv(
    DATA_DIR / "escenario_riesgo.csv",
    index=False
)
