from typing import Literal


def escape_triple_quotes(string: str, single_quote: Literal["'", '"'] = '"') -> str:
    """Escape triple quotes inside a string

    :param string: string to escape
    :param single_quote: single-quote character
    :return: escaped string
    """
    assert len(single_quote) == 1
    quote = "".join([single_quote] * 3)

    escaped_single_quote = rf"\{single_quote}"
    escaped_quote = "".join([escaped_single_quote] * 3)
    return string.replace(quote, escaped_quote)
