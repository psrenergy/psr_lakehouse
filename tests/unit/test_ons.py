import pandas as pd

import psr.lakehouse

expected_index = pd.MultiIndex.from_tuples(
    [
        (pd.to_datetime("2023-05-01"), "NORTH"),
        (pd.to_datetime("2023-05-01"), "NORTHEAST"),
        (pd.to_datetime("2023-05-01"), "SOUTHEAST"),
        (pd.to_datetime("2023-05-01"), "SOUTH"),
    ],
    names=["reference_date", "subsystem"],
)


def test_ons_max_stored_energy():
    df = psr.lakehouse.ons.max_stored_energy(
        start_reference_date="2023-05-01",
        end_reference_date="2023-05-02",
    )

    pd.testing.assert_index_equal(df.index, expected_index, check_exact=True)

    expected_series = pd.Series(
        [15302.396484, 51691.226562, 204615.328125, 20459.242188],
        index=expected_index,
        name="max_stored_energy",
    )
    pd.testing.assert_series_equal(df["max_stored_energy"], expected_series)


def test_ons_verified_stored_energy():
    df = psr.lakehouse.ons.verified_stored_energy_mwmonth(
        start_reference_date="2023-05-01",
        end_reference_date="2023-05-02",
    )

    expected_series = pd.Series(
        [15101.476562, 47018.351562, 176423.218750, 17171.507812],
        index=expected_index,
        name="verified_stored_energy_mwmonth",
    )
    pd.testing.assert_series_equal(df["verified_stored_energy_mwmonth"], expected_series)


def test_ons_verified_stored_energy_percentage():
    df = psr.lakehouse.ons.verified_stored_energy_percentage(
        start_reference_date="2023-05-01",
        end_reference_date="2023-05-02",
    )

    expected_series = pd.Series(
        [98.686996, 90.959999, 86.221901, 83.930298],
        index=expected_index,
        name="verified_stored_energy_percentage",
    )
    pd.testing.assert_series_equal(df["verified_stored_energy_percentage"], expected_series)

def test_ons_load_marginal_cost_weekly_average():
    df = psr.lakehouse.ons.load_marginal_cost_weekly_average(
        start_reference_date="2005-01-07",
        end_reference_date="2005-01-14",
    )
    
    expected_series = pd.Series(
        [0.94, 0.94, 0.00, 4.50],
        index=pd.MultiIndex.from_tuples(
            [
                (pd.to_datetime("2005-01-07"), "NORTH"),
                (pd.to_datetime("2005-01-07"), "NORTHEAST"),
                (pd.to_datetime("2005-01-07"), "SOUTHEAST"),
                (pd.to_datetime("2005-01-07"), "SOUTH"),
            ],
            names=["reference_date", "subsystem"],
        ),
        name="average",
    )
    pd.testing.assert_series_equal(df["average"], expected_series)

def test_ons_load_marginal_cost_weekly_light_load_segment():
    df = psr.lakehouse.ons.load_marginal_cost_weekly_light_load_segment(
        start_reference_date="2005-01-07",
        end_reference_date="2005-01-14",
    )

    print(df)

def test_ons_load_marginal_cost_weekly_medium_load_segment():
    df = psr.lakehouse.ons.load_marginal_cost_weekly_medium_load_segment(
        start_reference_date="2005-01-07",
        end_reference_date="2005-01-14",
    )

    print(df)

def test_ons_load_marginal_cost_weekly_heavy_load_segment():
    df = psr.lakehouse.ons.load_marginal_cost_weekly_heavy_load_segment(
        start_reference_date="2005-01-07",
        end_reference_date="2005-01-14",
    )

    print(df)