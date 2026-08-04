import matplotlib
matplotlib.use("Agg")  # headless backend so tests never try to open a GUI window

import pandas as pd
import matplotlib.pyplot as plt

from charts import plot_top_market_cap, plot_volume_vs_price_change, build_dashboard, format_usd

VALID_COIN = {
    "id": "bitcoin",
    "symbol": "btc",
    "current_price": 62000,
    "market_cap": 12_000_000_000,
    "total_volume": 45_000_000,
    "price_change_percentage_24h": 2.5,
    "market_cap_tier": "large_cap",
}


def make_coin(coin_id, market_cap, tier, total_volume=45_000_000, price_change=2.5):
    return {
        **VALID_COIN,
        "id": coin_id,
        "market_cap": market_cap,
        "market_cap_tier": tier,
        "total_volume": total_volume,
        "price_change_percentage_24h": price_change,
    }


def test_plot_top_market_cap_returns_fig_and_ax():
    df = pd.DataFrame([
        make_coin("bitcoin", 12_000_000_000, "large_cap"),
        make_coin("solana", 5_000_000_000, "mid_cap"),
    ])

    result = plot_top_market_cap(df)

    assert result is not None
    fig, ax = result
    assert fig is not None
    assert ax is not None
    plt.close(fig)


def test_plot_top_market_cap_limits_to_n():
    df = pd.DataFrame([
        make_coin(f"coin_{i}", 1_000_000_000 * (i + 1), "mid_cap")
        for i in range(15)
    ])

    fig, ax = plot_top_market_cap(df, n=10)

    assert len(ax.patches) == 10
    plt.close(fig)


def test_plot_top_market_cap_returns_none_on_empty_df():
    result = plot_top_market_cap(pd.DataFrame())
    assert result is None


def test_plot_volume_vs_price_change_returns_fig_and_ax():
    df = pd.DataFrame([
        make_coin("bitcoin", 12_000_000_000, "large_cap"),
        make_coin("pepe", 500_000_000, "small_cap"),
    ])

    result = plot_volume_vs_price_change(df)

    assert result is not None
    fig, ax = result
    assert len(ax.collections) == 2  # one scatter series per tier present
    plt.close(fig)


def test_plot_volume_vs_price_change_returns_none_without_tier_column():
    df = pd.DataFrame([make_coin("bitcoin", 12_000_000_000, "large_cap")]).drop(columns=["market_cap_tier"])

    result = plot_volume_vs_price_change(df)

    assert result is None


def test_plot_volume_vs_price_change_returns_none_on_empty_df():
    result = plot_volume_vs_price_change(pd.DataFrame())
    assert result is None


def test_build_dashboard_creates_png_file(tmp_path):
    df = pd.DataFrame([
        make_coin("bitcoin", 12_000_000_000, "large_cap"),
        make_coin("solana", 5_000_000_000, "mid_cap"),
        make_coin("pepe", 500_000_000, "small_cap"),
    ])
    output_path = tmp_path / "dashboard.png"

    result = build_dashboard(df, str(output_path))

    assert result == str(output_path)
    assert output_path.exists()
    plt.close("all")


def test_build_dashboard_returns_none_on_empty_df(tmp_path):
    result = build_dashboard(pd.DataFrame(), str(tmp_path / "dashboard.png"))
    assert result is None


def test_format_usd_trillions():
    assert format_usd(1_287_991_327_120) == "$1.3T"


def test_format_usd_billions():
    assert format_usd(5_000_000_000) == "$5.0B"


def test_format_usd_millions():
    assert format_usd(45_000_000) == "$45.0M"


def test_format_usd_below_million():
    assert format_usd(999) == "$999"
