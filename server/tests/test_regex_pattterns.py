import re

from cpho.util import get_regex_pattern


def test_all_regex_patterns():
    pattern_dict = get_regex_pattern("all")
    for pattern_item in pattern_dict.values():
        for valid_pattern in pattern_item["valid"]:
            assert re.match(pattern_item["pattern"], valid_pattern) is not None
