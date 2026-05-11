"""Deforestation Monitor PySpark Pipeline — Azure Databricks."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os


def get_spark():
    return SparkSession.builder.appName("DeforestationPipeline").getOrCreate()


def compute_annual_loss_rate(land_cover_df):
    w = Window.partitionBy("state").orderBy("year")
    return (
        land_cover_df
        .withColumn("prev_cover", F.lag("forest_cover_pct").over(w))
        .withColumn("annual_loss_pct", F.col("prev_cover") - F.col("forest_cover_pct"))
        .withColumn("cumulative_loss_pct",
                    F.sum("annual_loss_pct").over(w.rowsBetween(Window.unboundedPreceding, 0)))
        .withColumn("trend",
                    F.when(F.col("annual_loss_pct") > 1.5, "Rapid Loss")
                     .when(F.col("annual_loss_pct") > 0.8, "Moderate Loss")
                     .when(F.col("annual_loss_pct") > 0, "Slow Loss")
                     .otherwise("Stable/Gain"))
    )


def compute_carbon_stock_change(land_cover_df):
    w = Window.partitionBy("state").orderBy("year")
    return (
        land_cover_df
        .withColumn("prev_carbon", F.lag("carbon_stock_tco2_ha").over(w))
        .withColumn("carbon_flux_tco2_ha",
                    F.col("carbon_stock_tco2_ha") - F.col("prev_carbon"))
        .withColumn("total_carbon_lost",
                    F.col("carbon_flux_tco2_ha") * F.col("area_km2") * 100)
    )


if __name__ == "__main__":
    spark = get_spark()
    land_cover = spark.read.csv("data/land_cover.csv", header=True, inferSchema=True)
    loss_df = compute_annual_loss_rate(land_cover)
    carbon_df = compute_carbon_stock_change(land_cover)
    loss_df.show(10)
    carbon_df.show(10)
    spark.stop()
