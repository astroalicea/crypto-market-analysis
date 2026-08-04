import logging

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

logger = logging.getLogger(__name__)

TIER_COLORS = {
    "small_cap": "#4C72B0",
    "mid_cap": "#DD8452",
    "large_cap": "#55A868",
}


def format_usd(value, _position=None):
    for threshold, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if value >= threshold:
            return f"${value / threshold:.1f}{suffix}"
    return f"${value:,.0f}"


def plot_top_market_cap(df, n=10, ax=None):
    if df is None or df.empty:
        logger.error("Cannot plot top market cap on empty data.")
        return None

    if ax is None:
        _, ax = plt.subplots()

    # sort ascending so the largest coin ends up at the top of a horizontal bar chart
    top = df.sort_values("market_cap", ascending=False).head(n)
    top = top.sort_values("market_cap")

    ax.barh(top["symbol"].str.upper(), top["market_cap"])
    ax.set_xlabel("Market Cap (USD)")
    ax.set_title(f"Top {n} Coins by Market Cap")
    ax.xaxis.set_major_formatter(FuncFormatter(format_usd))
    return ax.figure, ax


def plot_volume_vs_price_change(df, ax=None):
    if df is None or df.empty:
        logger.error("Cannot plot volume vs. price change on empty data.")
        return None

    if "market_cap_tier" not in df.columns:
        logger.error("DataFrame missing market_cap_tier column. Run assign_market_cap_tiers first.")
        return None

    if ax is None:
        _, ax = plt.subplots()

    for tier, color in TIER_COLORS.items():
        subset = df[df["market_cap_tier"] == tier]
        if subset.empty:
            continue
        ax.scatter(
            subset["total_volume"],
            subset["price_change_percentage_24h"],
            label=tier,
            color=color,
        )

    ax.set_xlabel("24h Volume (USD)")
    ax.set_ylabel("24h Price Change (%)")
    ax.set_title("Volume vs. Price Change by Market Cap Tier")
    ax.xaxis.set_major_formatter(FuncFormatter(format_usd))
    ax.legend()
    return ax.figure, ax


def build_dashboard(df, output_path, n=10):
    if df is None or df.empty:
        logger.error("Cannot build dashboard on empty data.")
        return None

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    if plot_top_market_cap(df, n=n, ax=axes[0]) is None:
        return None
    if plot_volume_vs_price_change(df, ax=axes[1]) is None:
        return None

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    return output_path
