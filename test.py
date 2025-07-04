import pandas as pd
import psycopg
from unittest.mock import patch, MagicMock
from energy_data.main import get_dataframe

def main():
    df = get_dataframe()
    print(df)
