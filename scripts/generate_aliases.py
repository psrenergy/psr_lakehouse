from __future__ import annotations

import re
import textwrap
from pathlib import Path

import dotenv

from psr.lakehouse import client

dotenv.load_dotenv()

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "psr" / "lakehouse" / "alias.py"

INTERNAL_COLUMNS = {"id", "updated_at", "deleted_at"}

SKIP_TABLES = {"ceg", "ceg_data", "generator", "generator_generator_unit", "generator_unit"}


def to_snake(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def generate_method(table_name: str, schema: dict) -> str:
    columns = [col for col in schema if col not in INTERNAL_COLUMNS]
    columns_repr = repr(columns)

    method = textwrap.dedent(f"""\
    def {table_name}(self, **kwargs):
        return self.fetch_dataframe(table_name="{table_name}", data_columns={columns_repr}, **kwargs)
    """)
    return method


def generate_register_function(method_names: list[str]) -> str:
    lines = [
        "def register_aliases():",
        "    from psr.lakehouse.client import Client",
        "",
    ]
    for name in method_names:
        lines.append(f"    Client.{name} = {name}")
    return "\n".join(lines) + "\n"


def main():
    print("Discovering tables from API...")
    model_names = client.list_tables()
    print(f"Found {len(model_names)} tables")

    methods = []
    method_names = []

    for model_name in model_names:
        schema = client.get_schema(model_name)

        table_name = to_snake(model_name)
        if table_name in SKIP_TABLES:
            print(f"  Skipping {table_name}")
            continue

        print(f"  {table_name} ({len(schema)} columns)")
        methods.append(generate_method(table_name, schema))
        method_names.append(table_name)

    # Assemble output file
    header = textwrap.dedent("""\
    \"\"\"Auto-generated table alias methods for the PSR Lakehouse Client.

    DO NOT EDIT — regenerate with: make generate-aliases
    \"\"\"

    from __future__ import annotations

    """)

    output = header
    for method_src in methods:
        output += "\n" + method_src + "\n"
    output += "\n" + generate_register_function(method_names)

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"\nGenerated {len(method_names)} alias methods -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
