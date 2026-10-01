import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["id", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]

def load_coins_into_dataframe(coins):
    # .get() covers both a missing key and an explicit null — CoinGecko sends the latter for new/illiquid coins
    valid_coins = [coin for coin in coins if all(coin.get(field) is not None for field in REQUIRED_FIELDS)]

    dropped_count = len(coins) - len(valid_coins)
    if dropped_count:
        logger.warning(f"Dropped {dropped_count} of {len(coins)} coins with missing or null required fields.")

    if not valid_coins:
        logger.error("No valid coin data after field validation.")
        return None
    return pd.DataFrame(valid_coins)

def calculate_price_change_dispersion(df):
    # cross-sectional: how spread out the coins' 24h moves are at one moment.
    # Not volatility — that's one coin's returns over time, which needs snapshot history.
    if df is None or df.empty:
        logger.error("Cannot calculate price change dispersion on empty data.")
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

def assign_market_cap_tiers(df):
    if df is None or df.empty:
        logger.error("Cannot assign market cap tiers to empty data.")
        return None

    df = df.copy()
    # thresholds mirror industry-standard cap tiers, not relative to the fetched sample
    bins = [-np.inf, 1_000_000_000, 10_000_000_000, np.inf]
    labels = ["small_cap", "mid_cap", "large_cap"]
    df["market_cap_tier"] = pd.cut(df["market_cap"], bins=bins, labels=labels)
    return df
