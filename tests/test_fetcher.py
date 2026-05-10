import pytest
from unittest.mock import patch, MagicMock
from fetcher import fetch_coins

def test_fetch_coins_returns_list_on_success():
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "bitcoin", "symbol": "btc"}]
    mock_response.raise_for_status.return_value = None

    with patch("fetcher.requests.get", return_value=mock_response):
        result = fetch_coins()

    assert result == [{"id": "bitcoin", "symbol": "btc"}]