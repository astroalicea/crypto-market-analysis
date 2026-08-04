import pytest

from dashboard.models import CoinSnapshot


@pytest.mark.django_db
def test_coin_snapshot_saves_and_reads_back():
    snapshot = CoinSnapshot.objects.create(
        coin_id="bitcoin",
        symbol="btc",
        current_price="62000.12345678",
        market_cap="1200000000000.00",
        total_volume="45000000000.00",
        price_change_percentage_24h=2.5,
        market_cap_tier="large_cap",
    )

    saved = CoinSnapshot.objects.get(id=snapshot.id)

    assert saved.coin_id == "bitcoin"
    assert saved.symbol == "btc"
    assert str(saved.current_price) == "62000.12345678"
    assert saved.market_cap_tier == "large_cap"
    assert saved.fetched_at is not None


@pytest.mark.django_db
def test_coin_snapshot_str_representation():
    snapshot = CoinSnapshot.objects.create(
        coin_id="bitcoin",
        symbol="btc",
        current_price="62000",
        market_cap="1200000000000",
        total_volume="45000000000",
        price_change_percentage_24h=2.5,
        market_cap_tier="large_cap",
    )

    assert "BTC" in str(snapshot)


@pytest.mark.django_db
def test_coin_snapshot_orders_newest_first():
    older = CoinSnapshot.objects.create(
        coin_id="bitcoin",
        symbol="btc",
        current_price="60000",
        market_cap="1100000000000",
        total_volume="40000000000",
        price_change_percentage_24h=1.0,
        market_cap_tier="large_cap",
    )
    newer = CoinSnapshot.objects.create(
        coin_id="bitcoin",
        symbol="btc",
        current_price="62000",
        market_cap="1200000000000",
        total_volume="45000000000",
        price_change_percentage_24h=2.5,
        market_cap_tier="large_cap",
    )

    results = list(CoinSnapshot.objects.all())

    assert results[0].id == newer.id
    assert results[1].id == older.id
