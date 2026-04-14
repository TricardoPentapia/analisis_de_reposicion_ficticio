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

    def cargar_data(self):
        self.productos = pd.read_csv(self.data_dir / "productos.csv")
        self.ventas = pd.read_csv(self.data_dir / "ventas.csv", parse_dates=["fecha"])
        self.inventario = pd.read_csv(self.data_dir / "inventario.csv")

    def preparar_data_demanda(self):
        self.demanda_stats = (self.ventas.groupby(["store_id", "producto_id"])["unidades_vendidas"].agg(demanda_promedio_diaria="mean",demanda_std_diaria="std").reset_index())

        self.demanda_stats["demanda_std_diaria"] = (self.demanda_stats["demanda_std_diaria"].fillna(0))

    def build_base_dataframe(self):
        self.base_df = (self.inventario.merge(self.demanda_stats, on=["store_id", "producto_id"], how="left").merge(self.productos[["producto_id", "categoria", "tiempo_entrega_dias", "precio_venta"]],
                on="producto_id",
                how="left"
            )
        )

        self.base_df["stock_total"] = (
            self.base_df["stock_disponible"] + self.base_df["stock_transito"]
        )

    def calcular_days_of_supply(self):
        self.base_df["days_of_supply"] = np.where(
            self.base_df["demanda_promedio_diaria"] > 0,
            self.base_df["stock_total"] / self.base_df["demanda_promedio_diaria"],
            np.nan
        )

    def calcular_stock_seguridad(self):
        self.base_df["stock_seguridad"] = (
            self.service_level_z
            * self.base_df["demanda_std_diaria"]
            * np.sqrt(self.base_df["tiempo_entrega_dias"])
        ).round()

    def calcular_logica_reorden(self):
        self.base_df["reorder_point"] = (
            self.base_df["demanda_promedio_diaria"] * self.base_df["tiempo_entrega_dias"]
            + self.base_df["stock_seguridad"]
        )

        self.base_df["stock_objetivo"] = (
            self.base_df["demanda_promedio_diaria"] * self.cobertura_objetivo
            + self.base_df["stock_seguridad"]
        )

        self.base_df["cantidad_pedir"] = (
            self.base_df["stock_objetivo"] - self.base_df["stock_total"]
        ).clip(lower=0).round()

        self.base_df["accion"] = np.where(
            self.base_df["stock_total"] <= self.base_df["reorder_point"],
            "REORDENAR",
            "OK"
        )

    def generar_reporte(self):
        self.base_df.to_csv(self.output_dir / "reporte_reposicion.csv", index=False)

        productos_a_pedir = self.base_df[self.base_df["accion"] == "REORDENAR"].copy()
        productos_a_pedir.to_csv(self.output_dir / "productos_a_pedir.csv", index=False)

        top_riesgo = (
            self.base_df
            .sort_values("days_of_supply")
            [[
                "store_id",
                "producto_id",
                "categoria",
                "days_of_supply",
                "stock_total",
                "demanda_promedio_diaria",
                "accion",
                "cantidad_pedir"
            ]]
            .head(20)
        )
        top_riesgo.to_csv(self.output_dir / "top_riesgo.csv", index=False)

        resumen_tienda = (
            self.base_df
            .groupby("store_id")
            .agg(
                sku_totales=("producto_id", "count"),
                sku_a_reordenar=("accion", lambda x: (x == "REORDENAR").sum()),
                cantidad_total_pedir=("cantidad_pedir", "sum")
            )
            .reset_index()
        )
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