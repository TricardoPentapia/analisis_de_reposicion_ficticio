import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np 
import math

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
    
# DOS (Days of Supply) | merge de inventario con demanda_prom ( ventas ) y con productos
dos_df = (inventario.merge(demanda_prom, on=["store_id", "producto_id"], how="left"))
# Calculo de stock total
dos_df["stock_total"] = dos_df["stock_disponible"] + dos_df["stock_transito"]

# Calculo del days of supply
dos_df["dos"] = np.where(dos_df["demanda_promedio_diaria"] > 0, dos_df["stock_total"] / dos_df["demanda_promedio_diaria"], np.nan)

# gráfico de dos promedio por categoria
for store_id in dos_df["store_id"].unique():
    #agrupamos por tienda para el gráfico y sacamos el promedos del dos
    dos_por_tienda  = (dos_df[dos_df["store_id"] == store_id].groupby("categoria")["dos"].mean().sort_values())
    
    #gráfico
    plt.figure(figsize=(10, 5))
    ax = dos_por_tienda.plot(kind="bar")
    plt.axhline(7, linestyle="--", linewidth=1) # linea para marcar 7 días de supply
    plt.axhline(20, linestyle="--", linewidth=1) # linea para marcar 20 días de supply 
    plt.title(f"dos promedio por categoria - tienda {store_id}") 
    plt.ylabel("Días de cobertura")
    plt.xlabel("Categoria")
    plt.xticks(rotation=45, ha="right")
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
    plt.tight_layout()
    plt.savefig(output_dir / f"dos_categoria_por_tienda_{store_id}.png")
    plt.close()
    
# gráfico general
dos_general = (dos_df.groupby("categoria")["dos"].mean().sort_values())
plt.figure(figsize=(10, 5))
ax = dos_general.plot(kind="bar")
plt.title(f"Demanda promedio por categoria - general")
plt.ylabel("Días de cobertura")
plt.xlabel("Categoria")
plt.xticks(rotation=45, ha="right")
ax.bar_label(ax.containers[0],fmt="%.1f", padding=3)
plt.tight_layout()
plt.savefig(output_dir / f"dos_categoria_general.png")
plt.close()

# top 10 riesgo
df_10_riesgo = dos_general.head(10)

# ROP
df_reorder = dos_df.merge(productos[["producto_id", "tiempo_entrega_dias"]], on="producto_id", how="left")
df_reorder["reorder_point"] = (df_reorder["demanda_promedio_diaria"] * df_reorder["tiempo_entrega_dias"])
df_reorder["accion"] = np.where(df_reorder["stock_total"] <= df_reorder["reorder_point"], "Reordenar", "ok")

# Cantidad a pedir
dias_de_cobertura_obj = 20 # supondremos que buscaremos un inventario para unos 20 dias app
df_reorder["stock_objetivo"] = np.ceil((df_reorder["demanda_promedio_diaria"] * dias_de_cobertura_obj))
df_reorder["cantidad_pedir"] = np.ceil(df_reorder["stock_objetivo"] - df_reorder["stock_total"]).clip(lower=0)

# export del df de reorder
df_reorder.to_csv("outputs/reporte_reposición_final.csv", index=False)


