import pandas as pd


def today() -> pd.Timestamp:
    return pd.Timestamp(pd.Timestamp.today(), tz="UTC").normalize()


def tomorrow() -> pd.Timestamp:
    return pd.Timestamp(
        pd.Timestamp.today() + pd.Timedelta(days=1), tz="UTC"
    ).normalize()


def check_start(check_date: str = "2024-04-01") -> pd.Timestamp:
    return pd.Timestamp(check_date, tz="UTC").normalize()
