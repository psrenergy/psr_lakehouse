#!/usr/bin/env python3
"""Test script to verify the psr_lakehouse client works with the API."""

import os

# Set the API URL (adjust as needed)
os.environ["LAKEHOUSE_API_URL"] = "http://localhost:8000"

from psr.lakehouse import client
from psr.lakehouse.metadata import get_model_name

# Test model name conversion
print("=" * 60)
print("Testing model name conversion:")
print("=" * 60)
test_tables = [
    "ons_energy_load_daily",
    "ccee_spot_price",
    "ons_stored_energy_subsystem",
    "ons_power_plant_availability",
]
for table in test_tables:
    print(f"  {table} -> {get_model_name(table)}")

print()

# Test schema endpoints
print("=" * 60)
print("Testing schema endpoints:")
print("=" * 60)

print("\n1. List all models:")
try:
    models = client.list_models()
    print(f"   Found {len(models)} models")
    print(f"   First 10: {models[:10]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. List all tables:")
try:
    tables = client.list_tables()
    print(f"   Found {len(tables)} tables")
    print(f"   First 10: {tables[:10]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. Get schema for ONSEnergyLoadDaily:")
try:
    schema = client.get_model_schema("ONSEnergyLoadDaily")
    print(f"   Table name: {schema['table_name']}")
    print(f"   Columns: {[c['name'] for c in schema['columns']]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n4. Get table columns for ons_energy_load_daily:")
try:
    cols = client.get_table_columns("ons_energy_load_daily")
    print(cols.to_string())
except Exception as e:
    print(f"   Error: {e}")

print()

# Test data query
print("=" * 60)
print("Testing data query (ons_energy_load_daily):")
print("=" * 60)
try:
    df = client.fetch_dataframe(
        table_name="ons_energy_load_daily",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["energy_load"],
        start_reference_date="2023-05-01",
        end_reference_date="2023-05-02",
    )
    print(df.head(10))
    print(f"\nShape: {df.shape}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("Tests completed!")
print("=" * 60)
