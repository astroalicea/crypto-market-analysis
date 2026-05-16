import pytest
import pandas as pd
from analysis import load_coins_into_dataframe
from analysis import load_coins_into_dataframe, calculate_volatility, normalize_market_cap

VALID_COIN = {
    "id": "bitcoin",
    "symbol": "btc",
    "current_price": 62000,
    "market_cap": 1200000000,
    "total_volume": 45000000,
    "price_change_percentage_24h": 2.5
}
def make_coin(coin_id, market_cap):
    return {**VALID_COIN, "id": coin_id, "market_cap": market_cap}


def test_normalized_market_cap_adds_normalized_column():
    df = pd.DataFrame([
        make_coin("bitcoin", 1200000000),
        make_coin("ethereum", 370000000),
        make_coin("solana", 65000000),
    ])

    result = normalize_market_cap(df)

    assert"market_cap_normalized" in result.columns
    assert result["market_cap_normalized"].between(0, 1).all()

def test_normalize_market_cap_max_is_one_min_is_zero():
    df = pd.DataFrame([
        make_coin("bitcoin", 1200000000),
        make_coin("solana", 65000000),
    ])

    result = normalize_market_cap(df)

    assert result["market_cap_normalized"].max() == 1.0
    assert result["market_cap_normalized"].min() == .0

def test_normalize_market_cap_returns_none_when_all_identical():
    df = pd.DataFrame([
        make_coin("bitcoin", 1000000),
        make_coin("ethereum", 1000000),
    ])                      

    result = normalize_market_cap(df)

    assert result is None


def test_load_coins_returns_dataframe_on_valid_data():
    result = load_coins_into_dataframe([VALID_COIN])

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1

def test_load_coins_filters_out_invalid_coins():
    invalid_coin = {"id": "dogecoin", "symbol": "doge"}

    result = load_coins_into_dataframe([VALID_COIN, invalid_coin])

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["id"] == "bitcoin"

def test_load_coins_returns_none_when_all_invalid():
    invalid_coin = {"id": "dogecoin", "symbol": "doge"}

    result = load_coins_into_dataframe([invalid_coin])

    assert result is None

def test_calculate_volatility_returns_float():
    df = pd.DataFrame([
        {**VALID_COIN, "price_change_percentage_24h": 2.5},
        {**VALID_COIN, "id": "ethereum", "price_change_percentage_24h": -1.5},
        {**VALID_COIN, "id": "solana", "price_change_percentage_24h": 4.0},
    ])

    result = calculate_volatility(df)

    assert isinstance(result, float)
    assert result >= 0

def test_calculate_volatility_returns_none_on_none_input():
    result = calculate_volatility(None)

    assert result is None

def test_callculate_volatility_returns_none_on_empty_dataframe():
    result = calculate_volatility(pd.DataFrame())
    assert result is None