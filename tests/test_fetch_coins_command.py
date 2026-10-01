from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.db import DatabaseError

from dashboard.models import CoinSnapshot, FetchRun

VALID_COIN = {
    "id": "bitcoin",
    "symbol": "btc",
    "current_price": 62000,
    "market_cap": 1_200_000_000_000,
    "total_volume": 45_000_000_000,
    "price_change_percentage_24h": 2.5,
}


def make_coin(coin_id, market_cap):
    return {**VALID_COIN, "id": coin_id, "market_cap": market_cap}


@pytest.mark.django_db
def test_fetch_coins_command_saves_snapshots():
    coins = [
        make_coin("bitcoin", 1_200_000_000_000),
        make_coin("pepe", 500_000_000),
    ]

    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=coins,
    ):
        call_command("fetch_coins")

    assert CoinSnapshot.objects.count() == 2
    bitcoin = CoinSnapshot.objects.get(coin_id="bitcoin")
    assert bitcoin.market_cap_tier == "large_cap"
    pepe = CoinSnapshot.objects.get(coin_id="pepe")
    assert pepe.market_cap_tier == "small_cap"

    fetch_run = FetchRun.objects.get()
    assert fetch_run.status == FetchRun.Status.SUCCESS
    assert fetch_run.coins_requested == 20
    assert fetch_run.coins_saved == 2
    assert fetch_run.finished_at is not None
    assert set(fetch_run.snapshots.values_list("coin_id", flat=True)) == {"bitcoin", "pepe"}


@pytest.mark.django_db
def test_fetch_coins_command_handles_fetch_failure():
    stderr = StringIO()

    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=None,
    ):
        call_command("fetch_coins", stderr=stderr)

    assert CoinSnapshot.objects.count() == 0
    assert "Fetch failed" in stderr.getvalue()

    fetch_run = FetchRun.objects.get()
    assert fetch_run.status == FetchRun.Status.FAILED
    assert "Fetch failed" in fetch_run.error_message


@pytest.mark.django_db
def test_fetch_coins_command_handles_no_valid_coins():
    stderr = StringIO()
    invalid_coin = {"id": "dogecoin", "symbol": "doge"}

    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=[invalid_coin],
    ):
        call_command("fetch_coins", stderr=stderr)

    assert CoinSnapshot.objects.count() == 0
    assert "No valid coin data" in stderr.getvalue()
    assert FetchRun.objects.get().status == FetchRun.Status.FAILED


@pytest.mark.django_db
def test_fetch_coins_command_skips_coin_with_null_value_instead_of_crashing():
    null_change_coin = {**make_coin("newcoin", 500_000_000), "price_change_percentage_24h": None}

    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=[make_coin("bitcoin", 1_200_000_000_000), null_change_coin],
    ):
        call_command("fetch_coins")

    assert list(CoinSnapshot.objects.values_list("coin_id", flat=True)) == ["bitcoin"]


@pytest.mark.django_db
def test_fetch_coins_command_passes_per_page_argument():
    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=[make_coin("bitcoin", 1_200_000_000_000)],
    ) as mock_fetch:
        call_command("fetch_coins", "--per-page", "5")

    mock_fetch.assert_called_once_with(per_page=5)


@pytest.mark.django_db
def test_fetch_coins_command_marks_run_failed_on_database_error():
    stderr = StringIO()

    with patch(
        "dashboard.management.commands.fetch_coins.fetch_coins_from_api",
        return_value=[make_coin("bitcoin", 1_200_000_000_000)],
    ), patch(
        "dashboard.management.commands.fetch_coins.CoinSnapshot.objects.bulk_create",
        side_effect=DatabaseError("disk full"),
    ):
        call_command("fetch_coins", stderr=stderr)

    fetch_run = FetchRun.objects.get()
    assert fetch_run.status == FetchRun.Status.FAILED
    assert "disk full" in fetch_run.error_message
    assert CoinSnapshot.objects.count() == 0
