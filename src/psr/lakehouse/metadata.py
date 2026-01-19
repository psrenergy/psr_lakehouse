def get_model_name(table_name: str) -> str:
    """
    Convert a table name to the corresponding API model name.

    Args:
        table_name: Snake_case table name (e.g., "ccee_spot_price")

    Returns:
        CamelCase model name (e.g., "CCEESpotPrice")
    """

    if "_" not in table_name:
        return table_name

    # Fallback: convert snake_case to PascalCase
    # Special handling for organization prefixes (ONS, CCEE) that should remain uppercase
    UPPERCASE_PREFIXES = {"ons", "ccee"}

    words = table_name.split("_")
    result = []
    for word in words:
        if word.lower() in UPPERCASE_PREFIXES:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return "".join(result)
