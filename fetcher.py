import requests
import logging

logger = logging.getLogger(__name__)

def fetch_coins(vs_currency="usd", per_page=10):
    base_url = "https://api.coingecko.com/api/v3"
    url = f"{base_url}/coins/markets"

    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request times out. CoinGecko did not respond in time.")
        return None
    except requests.exceptions.HTTPError as error:
        logger.error(f"HTTP error: {error}")
        return None
    except requests.exceptions.RequestException as error:
        logger.error(f"Request failed: {error}")
        return None
