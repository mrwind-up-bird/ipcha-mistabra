# ipcha/utils/models.py

import re

def get_model_family(model_name: str) -> str:
    """
    Extracts the model family from a model name string using a heuristic.

    The family is defined as the substring preceding the first digit or hyphen.
    Examples:
        - 'gpt-4o' -> 'gpt'
        - 'claude-3-opus-20240229' -> 'claude'
        - 'gemini-1.5-pro' -> 'gemini'

    Args:
        model_name: The full model name string.

    Returns:
        The extracted model family name.
    """
    if not isinstance(model_name, str) or not model_name:
        return ""

    # Split at the first occurrence of a digit or a hyphen.
    # The family is the first part of the split.
    parts = re.split(r'[0-9-]', model_name, maxsplit=1)
    return parts[0]
