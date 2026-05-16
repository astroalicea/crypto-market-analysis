import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["id", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]

def load_coins_into_dataframe(coins):
    valid_coins = [coin for coin in coins if all(field in coin for field in REQUIRED_FIELDS)]

    if not valid_coins:
        logger.error("No valid coin data after field validation.")
        return None
    return pd.DataFrame(valid_coins)

def calculate_volatility(df):
    if df is None or df.empty:
        logger.error("Cannot calculate volatility on empty data.")
        return None
    return float(np.std(df["price_change_percentage_24h"]))

def normalize_market_cap(df):
    if df is None or df.empty:
        logger.error("Cannot normalize empty data.")
        return None
    
    min_cap = df["market_cap"].min()
    max_cap = df["market_cap"].max()

    if min_cap == max_cap:
        logger.error("Cannot normalize: all market cap values are identical.")
        return None
    
    df = df.copy()
    df["market_cap_normalized"] = (df["market_cap"] - min_cap) / (max_cap - min_cap)
    return df
