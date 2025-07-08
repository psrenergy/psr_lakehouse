import psr.lakehouse

import pandas as pd

def test_ccee_spot_price():
    df = psr.lakehouse.ccee.spot_price(
        start_reference_date="2023-05-01 03:00:00",
        end_reference_date="2023-05-01 04:00:00",
    )

    expected_index = pd.MultiIndex.from_tuples(
        [
            (pd.to_datetime("2023-05-01 03:00:00"), "NORTH"),
            (pd.to_datetime("2023-05-01 03:00:00"), "NORTHEAST"),
            (pd.to_datetime("2023-05-01 03:00:00"), "SOUTHEAST"),
            (pd.to_datetime("2023-05-01 03:00:00"), "SOUTH"),
        ],
        names=["reference_date", "subsystem"],
    )
    pd.testing.assert_index_equal(df.index, expected_index, check_exact=True)

    expected_series = pd.Series([69.04, 69.04, 69.04, 69.04], index=expected_index, name="spot_price")
    pd.testing.assert_series_equal(df["spot_price"], expected_series)

