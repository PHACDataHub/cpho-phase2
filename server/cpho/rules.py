from server.rules_framework import add_rule, auto_rule


@auto_rule
def is_admin(user):
    return user.username == "admin"


def is_hso(user):
    return user.username == "hso"


def is_program(user):
    return user.username == "program"


def is_lead_for_branch(user):
    return True


def indicator_of_users_branch(user, indicator):
    """
    TODO: implement this rule
    """
    return True


def can_edit_indicator(user, indicator):
    return (
        user.is_admin
        or user.is_hso
        or (user.is_program and indicator_of_users_branch(user, indicator))
    )
