import pytest
from django.urls import reverse

from dashboard.models import CoinSnapshot, FetchRun


def make_run(status=FetchRun.Status.SUCCESS):
    return FetchRun.objects.create(coins_requested=20, status=status)


def make_snapshot(coin_id, market_cap, tier, fetch_run):
    return CoinSnapshot.objects.create(
        fetch_run=fetch_run,
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
def test_dashboard_view_shows_only_latest_successful_run(client):
    older_run = make_run()
    make_snapshot("bitcoin", 1_000_000_000_000, "large_cap", older_run)
    make_snapshot("pepe", 500_000_000, "small_cap", older_run)  # falls out of the top N next run
    newer_run = make_run()
    newer_bitcoin = make_snapshot("bitcoin", 1_200_000_000_000, "large_cap", newer_run)

    response = client.get(reverse("dashboard"))

    assert response.status_code == 200
    assert [s.id for s in response.context["snapshots"]] == [newer_bitcoin.id]


@pytest.mark.django_db
def test_dashboard_view_ignores_failed_runs(client):
    good_run = make_run()
    good_bitcoin = make_snapshot("bitcoin", 1_200_000_000_000, "large_cap", good_run)
    make_run(status=FetchRun.Status.FAILED)

    response = client.get(reverse("dashboard"))

    assert [s.id for s in response.context["snapshots"]] == [good_bitcoin.id]


@pytest.mark.django_db
def test_dashboard_chart_view_returns_png_when_data_exists(client):
    fetch_run = make_run()
    make_snapshot("bitcoin", 1_200_000_000_000, "large_cap", fetch_run)
    make_snapshot("pepe", 500_000_000, "small_cap", fetch_run)

    response = client.get(reverse("dashboard_chart"))

    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert len(response.content) > 0


@pytest.mark.django_db
def test_dashboard_chart_view_returns_no_content_when_empty(client):
    response = client.get(reverse("dashboard_chart"))

    assert response.status_code == 204
