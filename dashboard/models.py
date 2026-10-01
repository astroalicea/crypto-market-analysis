from django.db import models
from django.utils import timezone


class FetchRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running"
        SUCCESS = "success"
        FAILED = "failed"

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    coins_requested = models.PositiveIntegerField()
    coins_saved = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at", "-id"]  # id breaks ties between runs started in the same instant

    def __str__(self):
        return f"Run {self.id} ({self.status}) @ {self.started_at:%Y-%m-%d %H:%M}"

    def mark_succeeded(self, coins_saved):
        self.status = self.Status.SUCCESS
        self.coins_saved = coins_saved
        self.finished_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.finished_at = timezone.now()
        self.save()


class CoinSnapshot(models.Model):
    # nullable only because snapshots saved before FetchRun existed have no run
    fetch_run = models.ForeignKey(
        FetchRun,
        on_delete=models.CASCADE,
        related_name="snapshots",
        null=True,
        blank=True,
    )
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
