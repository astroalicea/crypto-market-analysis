import io

import matplotlib.pyplot as plt
import pandas as pd
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render

from charts import build_dashboard
from dashboard.models import CoinSnapshot, FetchRun


def _latest_snapshots():
    # only the newest *successful* run: coins that fell out of the top N disappear,
    # and a failed fetch leaves the last good data on screen instead of a blank page
    latest_run = FetchRun.objects.filter(status=FetchRun.Status.SUCCESS).first()
    if latest_run is None:
        return CoinSnapshot.objects.none()
    return latest_run.snapshots.order_by("-market_cap")


def _snapshots_to_dataframe(snapshots):
    df = pd.DataFrame(
        list(
            snapshots.values(
                "coin_id",
                "symbol",
                "current_price",
                "market_cap",
                "total_volume",
                "price_change_percentage_24h",
                "market_cap_tier",
            )
        )
    )
    if df.empty:
        return df

    # DB gives back Decimal objects; matplotlib/pandas math wants plain floats
    for column in ("current_price", "market_cap", "total_volume", "price_change_percentage_24h"):
        df[column] = df[column].astype(float)
    return df


def dashboard_view(request):
    snapshots = _latest_snapshots()
    context = {
        "snapshots": snapshots,
        "last_updated": snapshots.aggregate(latest=Max("fetched_at"))["latest"],
    }
    return render(request, "dashboard/index.html", context)


def dashboard_chart_view(request):
    df = _snapshots_to_dataframe(_latest_snapshots())
    buffer = io.BytesIO()

    if build_dashboard(df, buffer) is None:
        plt.close("all")
        return HttpResponse(status=204)

    plt.close("all")  # each request builds a new Figure; without this matplotlib leaks memory across requests
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")
