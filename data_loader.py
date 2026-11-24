"""Loads the NASA POWER csv file."""
from functools import lru_cache
import pandas as pd
from config import DATA_PATH


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Read the csv, skip the NASA header, fix missing values, add a DATE column."""
    with open(DATA_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    # NASA files start with a text header that ends with "-END HEADER-"
    header_end = next(i for i, line in enumerate(lines) if "-END HEADER-" in line)
    df = pd.read_csv(DATA_PATH, skiprows=header_end + 1)

    # NASA uses -999 for missing values
    df = df.replace(-999, float("nan"))

    # Build a real date from YEAR + day-of-year
    df["DATE"] = pd.to_datetime(df["YEAR"].astype(str), format="%Y") + pd.to_timedelta(df["DOY"] - 1, unit="D")
    df["MONTH"] = df["DATE"].dt.month
    return df
