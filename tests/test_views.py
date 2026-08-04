import pytest
from django.urls import reverse

from dashboard.models import CoinSnapshot


def make_snapshot(coin_id, market_cap, tier):
    return CoinSnapshot.objects.create(
        coin_id=coin_id,
        symbol=coin_id[:3],
        current_price="100.00",
        market_cap=str(market_cap),
        total_volume="1000000.00",
        price_change_percentage_24h=1.5,
        market_cap_tier=tier,
    )


@pytest.mark.django_db
def test_dashboard_view_shows_empty_state_with_no_data(client):
    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert b"No data yet" in response.content


@pytest.mark.django_db
def test_dashboard_view_lists_latest_snapshot_per_coin(client):
    older = make_snapshot("bitcoin", 1_000_000_000_000, "large_cap")
    newer = make_snapshot("bitcoin", 1_200_000_000_000, "large_cap")
    make_snapshot("pepe", 500_000_000, "small_cap")

    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    displayed_ids = {s.id for s in response.context["snapshots"]}
    assert newer.id in displayed_ids
    assert older.id not in displayed_ids


@pytest.mark.django_db
def test_dashboard_chart_view_returns_png_when_data_exists(client):
    make_snapshot("bitcoin", 1_200_000_000_000, "large_cap")
    make_snapshot("pepe", 500_000_000, "small_cap")

    response = client.get(reverse("dashboard_chart"))

    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert len(response.content) > 0


@pytest.mark.django_db
def test_dashboard_chart_view_returns_no_content_when_empty(client):
    response = client.get(reverse("dashboard_chart"))

    assert response.status_code == 204
