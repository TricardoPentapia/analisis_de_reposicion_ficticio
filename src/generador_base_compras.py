import pandas as pd
import numpy as np

# importamos la base de productos  
productos_df = pd.read_csv("Data/raw/productos.csv")
print(productos_df.head())