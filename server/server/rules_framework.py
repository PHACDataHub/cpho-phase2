# This module is a wrapper around the django-rules package
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

import rules
from rules import add_rule, predicate


class NonExistentRuleException(Exception):
    pass


# this is the "private" version, for mocking purposes
def _test_rule(name, user=None, obj=None):
    if not rules.rule_exists(name):
        raise NonExistentRuleException(f"rule {name} does not exist")
    else:
        return rules.test_rule(name, user, obj)


def test_rule(*args, **kwargs):
    return _test_rule(*args, **kwargs)


def auto_rule(fn):
    """
    shorthand, use as decorator, e.g.

    @auto_rule
    def rule_name(user, obj):
      ...



    """
    pred = predicate(fn)
    add_rule(fn.__name__, pred)
    return pred


def must_pass_rule(rule_name, raises_exception=False):
    """
    use as decorator on views, in between the view and the api decorator
    """

    def check_rule(user):
        if test_rule(rule_name, user):
            return True
        else:
            if raises_exception:
                raise PermissionDenied
            else:
                return False

    return user_passes_test(check_rule)
