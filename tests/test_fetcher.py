import pytest
import requests
from unittest.mock import patch, MagicMock
from fetcher import fetch_coins


def test_fetch_coins_returns_list_on_success():
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "bitcoin", "symbol": "btc"}]
    mock_response.raise_for_status.return_value = None

    with patch("fetcher.requests.get", return_value=mock_response):
        result = fetch_coins()

    assert result == [{"id": "bitcoin", "symbol": "btc"}]

def test_fetch_coins_returns_none_on_timeout():
    with patch("fetcher.requests.get", side_effect=requests.exceptions.Timeout):
        result = fetch_coins()

    assert result is None

def test_fetch_coins_return_none_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    with patch ("fetcher.requests.get", return_value=mock_response):
        result = fetch_coins()

    assert result is None
def test_fetch_coins_returns_none_on_request_exception():
    with patch("fetcher.requests.get", side_effect=requests.exceptions.ConnectionError):
        result = fetch_coins()

    assert result is None 