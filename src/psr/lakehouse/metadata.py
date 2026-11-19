from psr.lakehouse.connector import connector


def get_model_name(table_name: str) -> str:
    """
    Convert a table name to the corresponding API model name.

    Reads the names from the caller's plan (/query/whoami), initializing the connector on first
    use, so it needs LAKEHOUSE_API_URL and a token. A name outside the plan is guessed.

    Args:
        table_name: Snake_case table name (e.g., "ccee_spot_price")

    Returns:
        CamelCase model name (e.g., "CCEESpotPrice")
    """

    if "_" not in table_name:
        return table_name

    # The plan lists the real model names, whose acronyms are not spelled one way
    # (ABCPowerPlant beside AbcSpotPrice), so match on letters alone.
    key = table_name.replace("_", "").lower()
    for model_name in connector.whoami().get("tables") or []:
        if model_name.lower() == key:
            return model_name

    # A table outside the plan is a 404 whatever the guess; the guess only names it in that message.
    # Special handling for organization/source acronyms that should remain uppercase
    UPPERCASE_PREFIXES = {
        "ons",
        "ccee",
        "aneel",
        "redemet",
        "epe",
        "inmet",
        "anp",
        "bbce",
        "bcb",
        "cl_cen",
        "co_xm",
        "pe_coes",
    }

    words = table_name.split("_")
    result = []
    for word in words:
        if word.lower() in UPPERCASE_PREFIXES:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return "".join(result)
