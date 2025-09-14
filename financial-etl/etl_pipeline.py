import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from typing import List, Dict

# 1. Cargar configuración de API
load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# 2. Función Extract
def extract(symbol: str = "AAPL") -> pd.DataFrame:
    """
    Extrae datos diarios ajustados desde la API de Alpha Vantage.
    Args:
        symbol (str): El nombre de la acción (ej. 'AAPL', 'MSFT').
    Returns:
        pd.DataFrame: DataFrame con los datos crudos en formato string.
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",  # 20+ years of historical data.
        "apikey": API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Error al extraer datos: {data}")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df = df.rename_axis("date").reset_index()
    return df

# 3. Función Transform
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y convierte los tipos de datos del DataFrame extraído. Crea métricas específicas
    Args:
        df (pd.DataFrame): DataFrame crudo de la extracción.
    Returns:
        pd.DataFrame: DataFrame con columnas numéricas convertidas a float y fechas como datetime, ordenado de manera ascendente.
    """
    # Limpieza de datos
    df["date"] = pd.to_datetime(df["date"])
    numeric_cols = df.columns.drop("date")
    df[numeric_cols] = df[numeric_cols].astype(float)
    df = df.rename(columns={"1. open":"open","2. high":"high","3. low":"low","4. close":"close","5. volume":"volume"})
    df = df.sort_values("date")

    # Creación de métricas
    df["daily_return"] = df["close"].pct_change() # Rendimiento diario
    df["volatility_7d"] = df["daily_return"].rolling(window=7).std() # Volatilidad móvil (7 días)
    df["mean_20d"] = df["close"].rolling(window=20).mean() # Media móvil de 20 días
    df["mean_50d"] = df["close"].rolling(window=50).mean() # Media móvil de 50 días
    conditions = [ df["daily_return"] > 0.01, df["daily_return"] < -0.01] # Clasificación de ganacia o perdida
    choices = ["gain", "loss"]
    df["day_type"] = np.select(conditions, choices, default="neutral")

    return df

# 4. Función Load
def load(df: pd.DataFrame, symbol: str = "AAPL") -> None:
    """
    Guarda los datos transformados en un archivo CSV dentro de data/processed.
    Args:
        df (pd.DataFrame): DataFrame limpio con datos listos para análisis.
        symbol (str): Ticker de la acción, usado para nombrar el archivo.
    Returns:
        None
    """
    os.makedirs("data/processed", exist_ok=True)
    filepath = f"data/processed/{symbol}_daily.csv"
    df.to_csv(filepath, index=False)
    print(f"✅ Datos guardados en {filepath}")

# 5. Función para graficar resultados
def plot_data(df: pd.DataFrame) -> None:
    """
    Genera un gráfico del precio de cierre y medias móviles.
    Args:
        df (pd.DataFrame): DataFrame con columnas 'close', 'mean_20d' y 'mean_50d'.
    Returns:
        None
    """
    plt.figure(figsize=(12,6))
    plt.plot(df["date"], df["close"], label="Close Price", color="blue", alpha=0.6)
    plt.plot(df["date"], df["mean_20d"], label="MEAN 20 días", color="red", linestyle="--")
    plt.plot(df["date"], df["mean_50d"], label="MEAN 50 días", color="green", linestyle="--")

    plt.title("Precio de Cierre y Medias Móviles")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("outputs/closing_price_chart.png")
    plt.show()

    return None

# 5. Ejecución Pipeline
if __name__ == "__main__":
    symbol = "AAPL"  # puedes cambiarlo a MSFT, TSLA, etc.
    print(f"🚀 Iniciando ETL para {symbol}...")

    raw_df = extract(symbol)
    clean_df = transform(raw_df)
    load(clean_df, symbol)
    plot_data(clean_df)

    print(clean_df.head())
