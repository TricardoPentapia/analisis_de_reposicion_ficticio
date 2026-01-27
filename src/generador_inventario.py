import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(98)

# cargar los datasets 
productos_df = pd.read_csv("Data/raw/productos.csv")
tiendas_df= pd.read_csv("Data/raw/tiendas.csv")
ventas_df = pd.read_csv("Data/raw/ventas.csv", parse_dates=["fecha"])

# Supuestos (Politicas de inventario por categoría) días de covertura y probabilidad de existencias en tránsito
politica_inventario = {
    "Esmeriles": {"dias_covertura": (10,18), "transit_prob": 0.4},
    "Destornilladores manuales": {"dias_covertura": (15, 25), "transit_prob": 0.6},
    "Taladros": {"dias_covertura": (8, 15), "transit_prob": 0.5},
    "Sierras electricas": {"dias_covertura": (8,14), "transit_prob": 0.4},
    "Cepillos para madera": {"dias_covertura": (12, 20), "transit_prob": 0.5}
}

# supuesto de demanda, demanda promedio diaria por prooducto y por tienda
demanda_prom = (ventas_df.groupby(["store_id", "producto_id"])["unidades_vendidas"].mean().reset_index(name="demanda_promedio_diaria"))

# unir con productos
demanda_prom = demanda_prom.merge(productos_df[["producto_id", "categoria", "tiempo_entrega_dias"]],on="producto_id",how="left")

# generar inventario
inventario = []

snapshot_date = ventas_df["fecha"].max()

for _, row in demanda_prom.iterrows():
    
    categoria = row["categoria"]
    demanda = row["demanda_promedio_diaria"]
    tiempo_entrega = row["tiempo_entrega_dias"]
    
    politica = politica_inventario[categoria]
    
    cobertura = np.random.randint(*politica["dias_covertura"])
    stock_disponible = int(round(demanda * cobertura))
    
    if np.random.rand() < politica["transit_prob"]:
        stock_transito = int(round(demanda * tiempo_entrega))
    else:
        stock_transito= 0
        
    inventario.append({
        "fecha": snapshot_date,
        "store_id": row["store_id"],
        "producto_id": row["producto_id"],
        "stock_disponible": stock_disponible,
        "stock_transito": stock_transito
    })

# exportar inventario
inventario_df = pd.DataFrame(inventario)

output_dir = Path("Data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

inventario_df.to_csv(output_dir / "inventario.csv", index=False)

print(f"Registros de inventario: {len(inventario_df)}")
inventario_df.head()
