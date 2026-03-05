import os

import dotenv

from psr.lakehouse import client, initialize

dotenv.load_dotenv()

initialize(base_url="https://lakehouse.psr-inc.com")

# df = client.fetch_dataframe(
#     table_name="ccee_spot_price",
#     group_by=["reference_date", "subsystem"],
#     aggregation_method = "avg",
#     datetime_granularity="day",
#     start_reference_date="2025-01-01",
#     end_reference_date="2025-12-31"
# )

df = client.ons_energy_load_monthly()

# df = client.ccee_spot_price(
#     group_by=["reference_date", "subsystem"],
#     aggregation_method = "avg",
#     datetime_granularity="day",
#     start_reference_date="2025-01-01",
#     end_reference_date="2025-12-31"
# )

print(df.head())
