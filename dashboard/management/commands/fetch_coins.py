from django.core.management.base import BaseCommand

from analysis import assign_market_cap_tiers, load_coins_into_dataframe
from dashboard.models import CoinSnapshot
from fetcher import fetch_coins as fetch_coins_from_api


class Command(BaseCommand):
    help = "Fetch current market data from CoinGecko and store it as CoinSnapshot rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--per-page",
            type=int,
            default=20,
            help="Number of coins to fetch, ranked by market cap (default: 20).",
        )

    def handle(self, *args, **options):
        per_page = options["per_page"]

        coins = fetch_coins_from_api(per_page=per_page)
        if coins is None:
            self.stderr.write(self.style.ERROR("Fetch failed. See logs for details."))
            return

        df = load_coins_into_dataframe(coins)
        if df is None:
            self.stderr.write(self.style.ERROR("No valid coin data after field validation."))
            return

        df = assign_market_cap_tiers(df)
        if df is None:
            self.stderr.write(self.style.ERROR("Could not assign market cap tiers."))
            return

        snapshots = [
            CoinSnapshot(
                coin_id=str(row["id"]),
                symbol=str(row["symbol"]),
                current_price=str(row["current_price"]),
                market_cap=str(row["market_cap"]),
                total_volume=str(row["total_volume"]),
                price_change_percentage_24h=float(row["price_change_percentage_24h"]),
                market_cap_tier=str(row["market_cap_tier"]),
            )
            for _, row in df.iterrows()
        ]

        CoinSnapshot.objects.bulk_create(snapshots)

        self.stdout.write(self.style.SUCCESS(f"Saved {len(snapshots)} coin snapshots."))
