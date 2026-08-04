from django.db import models


class CoinSnapshot(models.Model):
    coin_id = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=25, decimal_places=2)
    total_volume = models.DecimalField(max_digits=25, decimal_places=2)
    price_change_percentage_24h = models.FloatField()
    market_cap_tier = models.CharField(max_length=20)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fetched_at"]

    def __str__(self):
        return f"{self.symbol.upper()} @ {self.fetched_at:%Y-%m-%d %H:%M}"
