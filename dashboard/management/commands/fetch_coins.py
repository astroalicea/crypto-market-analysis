from django.core.management.base import BaseCommand
from django.db import DatabaseError, transaction

from analysis import assign_market_cap_tiers, load_coins_into_dataframe
from dashboard.models import CoinSnapshot, FetchRun
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
        # created before fetching so failed runs are recorded too, not just successful ones
        fetch_run = FetchRun.objects.create(coins_requested=per_page)

        coins = fetch_coins_from_api(per_page=per_page)
        if coins is None:
            return self._fail(fetch_run, "Fetch failed. See logs for details.")

        df = load_coins_into_dataframe(coins)
        if df is None:
            return self._fail(fetch_run, "No valid coin data after field validation.")

        df = assign_market_cap_tiers(df)
        if df is None:
            return self._fail(fetch_run, "Could not assign market cap tiers.")

        snapshots = [
            CoinSnapshot(
                fetch_run=fetch_run,
                coin_id=str(coin["id"]),
                symbol=str(coin["symbol"]),
                current_price=str(coin["current_price"]),
                market_cap=str(coin["market_cap"]),
                total_volume=str(coin["total_volume"]),
                price_change_percentage_24h=float(coin["price_change_percentage_24h"]),
                market_cap_tier=str(coin["market_cap_tier"]),
            )
            for coin in df.to_dict("records")
        ]

        try:
            # snapshots and the success status land together, or neither does
            with transaction.atomic():
                CoinSnapshot.objects.bulk_create(snapshots)
                fetch_run.mark_succeeded(coins_saved=len(snapshots))
        except DatabaseError as error:
            return self._fail(fetch_run, f"Database error while saving snapshots: {error}")

        self.stdout.write(self.style.SUCCESS(f"Run {fetch_run.id}: saved {len(snapshots)} coin snapshots."))

    def _fail(self, fetch_run, error_message):
        fetch_run.mark_failed(error_message)
        self.stderr.write(self.style.ERROR(f"Run {fetch_run.id} failed: {error_message}"))
