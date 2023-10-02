"""Backported `Template` Class utilities for Python < 3.11."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from string import Template


def is_valid(template: Template) -> bool:
    """
    Check if a template pattern is valid.
    Args:
        template (Template): A Template object containing the pattern to search.

    Returns:
        bool: True if the given template is valid, otherwise False.

    Remarks:
        This is Python 3.11 backport of `Template.is_valid` method
    Author: Python Software Foundation
    """
    for mo in template.pattern.finditer(template.template):
        if mo.group("invalid") is not None:
            return False
        if (
            mo.group("named") is None
            and mo.group("braced") is None
            and mo.group("escaped") is None
        ):
            # If all the groups are None, there must be
            # another group we're not expecting
            raise ValueError(f"Unrecognized named group in pattern: {template.pattern}")
    return True


def get_identifiers(template: Template) -> list[str]:
    """
    Extract and return a list of unique named identifiers from a template pattern.

    This function searches for named identifiers within the given template pattern
    and returns them as a list.
    Args:
        template (Template): A Template object containing the pattern to search.

    Returns:
        List[str]: A list of unique named identifiers found in the pattern.

    Raises:
        ValueError: If an unrecognized named group is found in the pattern, which
            means there may be an unexpected group in the regular expression pattern.

    Example:
        >>> template = Template(r'Hello, ${name}! My name is ${my_name}.')
        >>> get_identifiers(template)
        ['name', 'my_name']

    Remarks:
        This is Python 3.11 backport of `Template.get_identifiers` method
    Author: Python Software Foundation
    """
    ids: list[str] = []
    for mo in template.pattern.finditer(template.template):
        named = mo.group("named") or mo.group("braced")
        if named is not None and named not in ids:
            # add a named group only the first time it appears
            ids.append(named)
        elif (
            named is None
            and mo.group("invalid") is None
            and mo.group("escaped") is None
        ):
            # If all the groups are None, there must be
            # another group we're not expecting
            raise ValueError("Unrecognized named group in pattern", template.pattern)
    return ids
