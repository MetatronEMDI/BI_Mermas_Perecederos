from pathlib import Path
import pandas as pd
# Definir la ubicación de los archivos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Leer los primeros 10,000 registros de ventas
df_ventas = pd.read_csv(DATA_DIR / "train.csv", nrows=10000)

# Leer el catálogo completo de productos
df_productos = pd.read_csv(DATA_DIR / "items.csv")

# Mostrar dimensiones de los DataFrames
print("Dimensiones de ventas:", df_ventas.shape)
print("Dimensiones de productos:", df_productos.shape)

# Ver las primeras filas
print("\nPrimeras registros de ventas:")
print(df_ventas.head())
print("\nPrimeras registros de productos:")
print(df_productos.head())

print("\n Información de Ventas")
df_ventas.info()

print("\n Valores nulos en ventas:")
print(df_ventas.isnull().sum())

print("\n Información de productos")
df_productos.info()

print("\n Valores nulos en productos")
print(df_productos.isnull().sum())

# DISTRIBUCIÓN DE PRODUCTOS POR FAMILIA COMERCIAL
print("\n Productos por familias:")
print(df_productos["family"].value_counts())

# SELECCIÓN DE PRODUCTOS LACTEOS
df_dairy = df_productos[df_productos['family'] == 'DAIRY']
print("\n Total de productos lácteos:", len(df_dairy))

# VERIFICACION DE DATOS CLASIFICADOS COMO PERECEDEROS
print("\n Claisificación de Productos Perecederos:\n")
print(df_dairy['perishable'].value_counts())

# Familias de productos seleccionadas
familias = [
    "DAIRY",
    "PRODUCE",
    "BREAD/BAKERY",
    "MEATS",
    "POULTRY",
    "EGGS",
    "SEAFOOD"
]

# Filtrar catálogo de productos
df_perecederos = df_productos[
    df_productos["family"].isin(familias)
].copy()

# Verificar clasificación de perecibilidad
print("\nClasificación de perecibilidad por familia:")
print(pd.crosstab(
    df_perecederos["family"],
    df_perecederos["perishable"]
))

print("\nTotal de productos seleccionados:", len(df_perecederos))

# Identificar los productos perecederos seleccionados
mapa_familias = df_perecederos.set_index("item_nbr")["family"]

# Archivo donde guardaremos las ventas filtradas
salida = DATA_DIR / "ventas_perecederos.csv"

total = 0
primero = True

# Procesar las ventas históricas en bloques
for bloque in pd.read_csv(
    DATA_DIR / "train.csv",
    usecols=["date", "store_nbr", "item_nbr", "unit_sales", "onpromotion"],
    chunksize=250000
):

    # Conservar únicamente los productos seleccionados
    filtrado = bloque[bloque["item_nbr"].isin(mapa_familias.index)].copy()

    # Incorporar la familia comercial de cada producto
    filtrado["family"] = filtrado["item_nbr"].map(mapa_familias)

    # Guardar los registros filtrados
    filtrado.to_csv(
        salida,
        mode="w" if primero else "a",
        header=primero,
        index=False
    )

    total += len(filtrado)
    primero = False

print("\nTotal de registros de perecederos:", total)
print("Archivo generado:", salida)