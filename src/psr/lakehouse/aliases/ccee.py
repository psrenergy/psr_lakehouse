import pandas as pd
from ..client import client


def spot_price(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ccee_spot_price",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["spot_price"],
        **kwargs,
    )
