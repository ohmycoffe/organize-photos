from string import Template

from organize_photos.template_backport import get_identifiers, is_valid


def test_get_identifiers() -> None:
    pattern = "${year}/${year}${month}${day}${hour}${minute}${second}-${oldname}"
    tested = get_identifiers(Template(pattern))
    expected = ["year", "month", "day", "hour", "minute", "second", "oldname"]
    assert expected == tested


def test_is_valid_should_return_true_for_valid_pattern() -> None:
    valid_pattern = r"${name}/${year}"
    assert is_valid(Template(valid_pattern)) is True


def test_is_valid_should_return_false_for_invalid_pattern() -> None:
    invalid_pattern = r"${!month}"
    assert not is_valid(template=Template(invalid_pattern))
