import pandas as pd
import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["id", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"]

def load_coins_into_dataframe(coins):
    valid_coins = [coin for coin in coins if all(field in coin for field in REQUIRED_FIELDS)]

    if not valid_coins:
        logger.error("No valid coin data after field validation.")
        return None
    return pd.DataFrame(valid_coins)