import pandas as pd
import numpy as np
from pathlib import Path


class AnalisisReposicion:
    def __init__(self, data_dir="data/raw", output_dir="outputs", service_level_z=1.65, cobertura_objetivo=15):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.service_level_z = service_level_z
        self.cobertura_objetivo = cobertura_objetivo

        self.productos = None
        self.ventas = None
        self.inventario = None
        self.demanda_stats = None
        self.base_df = None

    # Cargar bases de datos
    def cargar_data(self):
        self.productos = pd.read_csv(self.data_dir / "productos.csv")
        self.ventas = pd.read_csv(self.data_dir / "ventas.csv", parse_dates=["fecha"])
        self.inventario = pd.read_csv(self.data_dir / "inventario.csv")

        if "precio_venta" in self.productos.columns and "costo_unitario" not in self.productos.columns:
            self.productos.rename(columns={"precio_venta": "costo_unitario"}, inplace=True)
            
        self.validar_datos()
        self.validar_calidad_datos()
        
    def validar_datos(self):
        archivos_requeridos = {
            "productos": self.data_dir / "productos.csv",
            "ventas": self.data_dir / "ventas.csv",
            "inventario": self.data_dir / "inventario.csv"
        }
        for nombre, ruta in archivos_requeridos.items():
            if not ruta.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
            
        columnas_productos = {"producto_id", "categoria", "tiempo_entrega_dias"}
        columnas_ventas = {"fecha", "store_id", "producto_id", "unidades_vendidas"}
        columnas_inventario = {"fecha", "store_id", "producto_id", "stock_disponible", "stock_transito"}
        
        faltantes_productos = columnas_productos - set(self.productos.columns)
        faltantes_ventas = columnas_ventas - set(self.ventas.columns)
        faltantes_inventario = columnas_inventario - set(self.inventario.columns)
        
        if faltantes_productos:
            raise ValueError(f"faltan columnas en productos.csv: {faltantes_productos}")
        if faltantes_ventas:
            raise ValueError(f"faltan columnas en ventas.csv: {faltantes_ventas}")
        if faltantes_inventario:
            raise ValueError(f"faltan columnas en inventario.csv: {faltantes_inventario}")
        
        if self.productos.empty:
            raise ValueError(f"productos.csv está vacio")
        if self.ventas.empty:
            raise ValueError(f"ventas.csv está vacio")
        if self.inventario.empty:
            raise ValueError(f"inventario.csv está vacio")
        
        
    def validar_calidad_datos(self):
        if self.productos["producto_id"].isna().any():
            raise ValueError("Hay producto_id nulos en productos.csv")
        if self.ventas[["store_id", "producto_id"]].isna().any().any():
            raise ValueError("Hay store_id o producto_id nulos en ventas.csv")
        if self.inventario[["store_id", "producto_id"]].isna().any().any():
            raise ValueError("Hay store_id o producto_id nulos en inventario.csv")
        if (self.productos["tiempo_entrega_dias"] <= 0).any():
            raise ValueError("Hay tiempo_entrega_dias menores o iguales a 0 en productos.csv")
        if (self.ventas["unidades_vendidas"] < 0).any():
            raise ValueError("Hay unidades vendidas en negativo en ventas.csv")
        if (self.inventario["stock_disponible"] < 0).any():
            raise ValueError("Hay stock disponible negativo en inventario.csv")
        if (self.inventario["stock_transito"] < 0).any():
            raise ValueError("Hay stock en tránsito negativo en inventario.csv")
        
        productos_validos = set(self.productos["producto_id"])
        
        productos_ventas_no_validos = set(self.ventas["producto_id"]) - productos_validos
        productos_inventario_no_validos = set(self.inventario["producto_id"]) - productos_validos
        
        if productos_ventas_no_validos:
            raise ValueError(f"hay producto_id en ventas.csv que no existen en productos.csv: {productos_ventas_no_validos}")
        if productos_inventario_no_validos:
            raise ValueError(f"hay producto_id en inventario.csv que no existen en productos.csv: {productos_inventario_no_validos}")
    
    def preparar_data_demanda(self):
        self.demanda_stats = (self.ventas.groupby(["store_id", "producto_id"])["unidades_vendidas"].agg(demanda_promedio_diaria="mean",demanda_std_diaria="std").reset_index())

        self.demanda_stats["demanda_std_diaria"] = (self.demanda_stats["demanda_std_diaria"].fillna(0))

    def build_base_dataframe(self):
        self.base_df = (self.inventario.merge(self.demanda_stats, on=["store_id", "producto_id"], how="left").merge(self.productos[["producto_id", "categoria", "tiempo_entrega_dias", "costo_unitario"]],on="producto_id",how="left"))

        self.base_df["stock_total"] = (self.base_df["stock_disponible"] + self.base_df["stock_transito"])

    def calcular_days_of_supply(self):
        self.base_df["days_of_supply"] = np.where(self.base_df["demanda_promedio_diaria"] > 0,self.base_df["stock_total"] / self.base_df["demanda_promedio_diaria"],np.nan)

    def calcular_stock_seguridad(self):
        self.base_df["stock_seguridad"] = (self.service_level_z * self.base_df["demanda_std_diaria"] * np.sqrt(self.base_df["tiempo_entrega_dias"])).round()

    def calcular_logica_reorden(self):
        self.base_df["reorder_point"] = (self.base_df["demanda_promedio_diaria"] * self.base_df["tiempo_entrega_dias"] + self.base_df["stock_seguridad"])
        self.base_df["stock_objetivo"] = (self.base_df["demanda_promedio_diaria"] * self.cobertura_objetivo+ self.base_df["stock_seguridad"])
        self.base_df["cantidad_pedir"] = (self.base_df["stock_objetivo"] - self.base_df["stock_total"]).clip(lower=0).round()
        self.base_df["accion"] = np.where(self.base_df["stock_total"] <= self.base_df["reorder_point"],"REORDENAR","OK")

    def generar_reporte(self):
        self.base_df.to_csv(self.output_dir / "reporte_reposicion.csv", index=False)

        productos_a_pedir = self.base_df[self.base_df["accion"] == "REORDENAR"].copy()
        productos_a_pedir.to_csv(self.output_dir / "productos_a_pedir.csv", index=False)

        top_riesgo = (self.base_df.sort_values("days_of_supply")[["store_id","producto_id","categoria","days_of_supply","stock_total","demanda_promedio_diaria","accion","cantidad_pedir"]].head(20))
        top_riesgo.to_csv(self.output_dir / "top_riesgo.csv", index=False)

        resumen_tienda = (self.base_df.groupby("store_id").agg(sku_totales=("producto_id", "count"),sku_a_reordenar=("accion", lambda x: (x == "REORDENAR").sum()),cantidad_total_pedir=("cantidad_pedir", "sum")).reset_index())
        resumen_tienda.to_csv(self.output_dir / "resumen_tienda.csv", index=False)

        resumen_categoria = (self.base_df.groupby("categoria").agg(sku_totales=("producto_id", "count"),sku_a_reordenar=("accion", lambda x: (x == "REORDENAR").sum()),cantidad_total_pedir=("cantidad_pedir", "sum")).reset_index())
        resumen_categoria.to_csv(self.output_dir / "resumen_categoria.csv", index=False)

    def run(self):
        self.cargar_data()
        self.preparar_data_demanda()
        self.build_base_dataframe()
        self.calcular_days_of_supply()
        self.calcular_stock_seguridad()
        self.calcular_logica_reorden()
        self.generar_reporte()