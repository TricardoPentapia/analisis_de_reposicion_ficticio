import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(98)

# importamos la base de productos  
productos_df = pd.read_csv("Data/raw/productos.csv")

# creamos la información de comportamiento de tiendas en un diccionario
tiendas = {
    "S001": "Grande",
    "S002": "Grande",
    "S003": "Mediana",
    "S004": "Mediana"
}

# comportamiento por tipo
muilt_tienda = {
    "Grande": 1.2,
    "Mediana": 0.85
}

# demanda por categoria
demanda_categoria = {
    "Esmeriles": {"base": 1.2, "volatibilidad": 0.6},
    "Destornilladores manuales": {"base": 4.5, "volatibilidad": 0.3},
    "Taladros": {"base": 0.8, "volatibilidad": 0.7},
    "Sierras electricas": {"base":0.6, "volatibilidad": 0.8},
    "Cepillos para madera": {"base": 1.0, "volatibilidad": 0.5}
}

# rango de fechas
fechas = pd.date_range(start="2024-01-01", periods=90, freq="D")

# generación de ventas
ventas = []

for fecha in fechas:
    for store_id, tipo_tienda in tiendas.items():
        for _, producto in productos_df.iterrows():
            
            cat = producto["categoria"]
            base = demanda_categoria[cat]["base"]
            volatibilidad = demanda_categoria[cat]["volatibilidad"]
            
            demanda_esperada = base * muilt_tienda[tipo_tienda]
            
            ruido = np.random.normal(1, volatibilidad)
            unidades = int(round(demanda_esperada * ruido))
            
            unidades = max(unidades, 0)
            
            ventas.append({
                "fecha": fecha,
                "store_id": store_id,
                "producto_id": producto["producto_id"],
                "unidades_vendidas": unidades
            })
            
# generar df y exp
ventas_df = pd.DataFrame(ventas)

output_dir = Path("data/raw")
ventas_df.to_csv(output_dir / "ventas.csv", index=False)

print(f"Ventas generadas: {len(ventas_df)} filas")
ventas_df.head()
