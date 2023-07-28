# this file is awkwardly named because it can't start with test_ or it will be picked up by pytest

from unittest.mock import patch

from server.rules_framework import _test_rule as real_test_rule


class patch_rules:
    """
    usage: with mock_rules(is_catalogue_admin=False):
      assert test_client.get(some_view_that_uses_patched_rules).status_code == 403
    """

    @staticmethod
    def rule_mocker(**rule_stubs):
        def exec_rule(rule_name, user=None, obj=None):
            if rule_name in rule_stubs:
                return rule_stubs[rule_name]
            else:
                return real_test_rule(rule_name, user, obj)

        return exec_rule

    def __init__(self, **rule_stubs):
        self._patch = patch(
            "server.rules_framework._test_rule", self.rule_mocker(**rule_stubs)
        )

    def __enter__(self):
        return self._patch.__enter__()

    def __exit__(self, *excp):
        return self._patch.__exit__(*excp)
