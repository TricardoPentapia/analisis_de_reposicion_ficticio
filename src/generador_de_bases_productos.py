import numpy as np
import pandas as pd

# establecer la semilla para mantener los datos aleatorios
np.random.seed(98)

# configuración de categorias para obtener el codigo de cada producto

configuracion_categorias = {
    "Esmeriles": {
        "prefijo": "ESM",
        "n_productos": 10,
        "rango_precios": (12990, 22990),
        "tiempo_entrega_dias": (2, 6)
    },
    "Destornilladores manuales": {
        "prefijo": "DES",
        "n_productos": 15,
        "rango_precios": (6990, 19990),
        "tiempo_entrega_dias": (1, 5)
    },
    "Taladros": {
        "prefijo": "TAL",
        "n_productos": 8,
        "rango_precios": (49990, 249990),
        "tiempo_entrega_dias": (2, 6)
    },
    "Sierras electricas": {
        "prefijo": "SIE",
        "n_productos": 6,
        "rango_precios": (69990, 199990),
        "tiempo_entrega_dias": (2, 6)
    },
    "Cepillos para madera": {
        "prefijo": "CEP",
        "n_productos": 5,
        "rango_precios": (39990, 249990),
        "tiempo_entrega_dias": (3, 8)
    }
}


# --------------------------------------------------
# Generación de productos
# --------------------------------------------------
productos = []

for categoria, config in configuracion_categorias.items():
    for i in range(1, config["n_productos"] + 1):

        producto_id = f"{config['prefijo']}-{i:03d}"
        precio_unitario = np.random.randint(*config["rango_precios"])
        tiempo_entrega = np.random.randint(*config["tiempo_entrega_dias"])

        productos.append({
            "producto_id": producto_id,
            "nombre_producto": f"{categoria} Producto {i}",
            "categoria": categoria,
            "marca": "Generica",
            "precio_venta": precio_unitario,
            "tiempo_entrega_dias": tiempo_entrega
        })

# --------------------------------------------------
# DataFrame y exportación
# --------------------------------------------------
productos_df = pd.DataFrame(productos)
productos_df.to_csv("data/raw/productos.csv", index=False)

print(f"Productos generados: {len(productos_df)}")
productos_df.head()
