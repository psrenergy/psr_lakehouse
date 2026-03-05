"""Generate alias methods for each table in the PSR Lakehouse API.

Connects to the live API, discovers tables via list_tables() and get_schema(),
and produces src/psr/lakehouse/alias.py with one method per table.

Requires LAKEHOUSE_API_URL environment variable to be set.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import dotenv

from psr.lakehouse import client
from psr.lakehouse.client import Client
from psr.lakehouse.metadata import get_model_name, get_table_name

dotenv.load_dotenv()

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "src" / "psr" / "lakehouse" / "alias.py"


def format_column_doc(col_name: str, col_info: dict) -> str:
    """Format a single column entry for the docstring."""
    col_type = col_info.get("type", "unknown")
    desc = col_info.get("description", col_info.get("title", ""))
    fmt = col_info.get("format", "")

    parts = [f"- **{col_name}**"]
    type_str = col_type
    if fmt:
        type_str += f" ({fmt})"
    parts.append(f" *{type_str}*")
    if desc:
        parts.append(f" — {desc}")
    if col_info.get("enum_values"):
        values = ", ".join(repr(v) for v in col_info["enum_values"])
        parts.append(f" [{values}]")
    return "".join(parts)


def generate_method(table_name: str, schema: dict) -> str:
    """Generate source code for a single alias method."""
    # Build column documentation
    column_lines = []
    for col_name, col_info in schema.items():
        if col_name in ("id", "updated_at", "deleted_at"):
            continue
        column_lines.append(format_column_doc(col_name, col_info))
    columns_doc = "\n".join(f"        {line}" for line in column_lines)

    method = textwrap.dedent(f"""\
    def {table_name}(self, **kwargs) -> "pd.DataFrame":
        \"\"\"Fetch data from the **{table_name}** table.

        Accepts the same keyword arguments as ``fetch_dataframe``
        (e.g. data_columns, filters, start_reference_date, …).

        Available columns:
{columns_doc}
        \"\"\"
        return self.fetch_dataframe(table_name="{table_name}", **kwargs)
    """)
    return method


def generate_register_function(method_names: list[str]) -> str:
    """Generate the register_aliases() function."""
    lines = [
        "def register_aliases():",
        '    """Attach all table alias methods to the Client class."""',
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

    # Collect existing Client method names to detect conflicts
    existing_methods = set(dir(Client))

    methods = []
    method_names = []
    skipped = []

    for model_name in model_names:
        table_name = get_table_name(model_name)

        # Validate roundtrip
        roundtrip = get_model_name(table_name)
        if roundtrip != model_name:
            print(f"  SKIP {model_name}: roundtrip failed ({table_name} -> {roundtrip})")
            skipped.append((model_name, f"roundtrip: {roundtrip}"))
            continue

        # Check for naming conflicts
        if table_name in existing_methods:
            print(f"  SKIP {model_name}: conflicts with existing Client.{table_name}")
            skipped.append((model_name, "name conflict"))
            continue

        # Fetch schema
        try:
            schema = client.get_schema(model_name)
        except Exception as e:
            print(f"  SKIP {model_name}: schema fetch failed ({e})")
            skipped.append((model_name, str(e)))
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

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        import pandas as pd

    """)

    output = header
    for method_src in methods:
        output += "\n" + method_src + "\n"
    output += "\n" + generate_register_function(method_names)

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"\nGenerated {len(method_names)} alias methods -> {OUTPUT_PATH}")

    if skipped:
        print(f"\nSkipped {len(skipped)} tables:")
        for name, reason in skipped:
            print(f"  {name}: {reason}")


if __name__ == "__main__":
    main()
