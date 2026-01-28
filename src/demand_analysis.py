import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


# cargamos las bases de inventario, productos, ventas y tiendas
inventario = pd.read_csv("data/raw/inventario.csv")
productos = pd.read_csv("data/raw/productos.csv")
ventas = pd.read_csv("data/raw/ventas.csv", parse_dates=["fecha"])

# análisis exploratorio
# calculamos la demanda promedio por producto y por tienda
demanda_prom = (ventas.groupby(["store_id", "producto_id"])["unidades_vendidas"].mean().reset_index(name="demanda_promedio_diaria"))

demanda_prom = demanda_prom.merge(productos[["producto_id", "categoria"]],on="producto_id",how="left") # Unión con la categoria

# realizaremos graficos por tienda y para eso calcularemos demanda general promedio por categoria
demanda_general_promedio = (demanda_prom.groupby("categoria")["demanda_promedio_diaria"].mean().sort_values(ascending=False))

#definimos la ruta de guardado con Path
output_dir = Path("outputs") #carpeta
output_dir.mkdir (parents=True, exist_ok=True) # si no existe, la crea

# graficamos la demanda general promedio
plt.figure(figsize=(10,5))
ax = demanda_general_promedio.plot(kind="bar")
plt.title("Demanda promedio diaria por categoría")
plt.ylabel("Unidades promedio por día")
plt.xlabel("Categoría")
plt.xticks(rotation=45, ha="right")

ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
plt.tight_layout()
plt.savefig(output_dir / "demanda_general_categoria.png") #guardado de la imagen de demanda general
plt.close()

# definiremos la demanda por tienda

for store_id in demanda_prom["store_id"].unique():

    demanda_tienda = (demanda_prom[demanda_prom["store_id"] == store_id].groupby("categoria")["demanda_promedio_diaria"].mean().sort_values(ascending=False))

    plt.figure(figsize=(10, 5))
    ax = demanda_tienda.plot(kind="bar")
    plt.title(f"Demanda promedio diaria por categoría – Tienda {store_id}")
    plt.ylabel("Unidades promedio por día")
    plt.xlabel("Categoría")
    plt.xticks(rotation=45, ha="right")
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
    plt.tight_layout()

    plt.savefig(output_dir / f"demanda_categoria_tienda_{store_id}.png")
    plt.close()