import pytest
import pandas as pd
from analysis import load_coins_into_dataframe

VALID_COIN = {
    "id": "bitcoin",
    "symbol": "btc",
    "current_price": 62000,
    "market_cap": 1200000000,
    "total_volume": 45000000,
    "price_change_percentage_24h": 2.5
}

def test_load_coins_returns_dataframe_on_valid_data():
    result = load_coins_into_dataframe([VALID_COIN])

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1