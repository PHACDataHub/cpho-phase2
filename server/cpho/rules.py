from server.rules_framework import add_rule, auto_rule


@auto_rule
def is_admin(user):
    return user.username == "admin"


def is_hso(user):
    return user.username == "hso"


def is_program(user):
    return user.username == "program"


def is_branch_lead(user):
    return True


def is_branch_user(user):
    return True


def is_branch_lead_or_user(user):
    return is_branch_user(user) or is_branch_lead(user)


def is_indicator_lead(user, indicator):
    return True


def indicator_of_users_branch(user, indicator):
    return True


def can_edit_indicator(user, indicator):
    return (
        is_admin(user)
        or is_hso(user)
        or (is_program(user) and is_indicator_lead(user, indicator))
        or (
            is_program(user)
            and is_branch_lead(user)
            and indicator_of_users_branch(user, indicator)
        )
    )


def can_submit_as_program(user, indicator):
    return (
        is_admin(user)
        or is_hso(user)
        or (is_program(user) and is_indicator_lead(user, indicator))
        # or (
        #     is_program(user)
        #     and is_branch_lead(user)
        #     and indicator_of_users_branch(user, indicator)
        # )
    )


def can_view_indicator(user, indicator):
    return (
        is_admin(user)
        or is_hso(user)
        or (is_program(user) and is_indicator_lead(user, indicator))
        or (
            is_program(user)
            and is_branch_lead_or_user(user)
            and indicator_of_users_branch(user, indicator)
        )
    )


def can_submit_as_hso(user):
    return is_admin(user) or is_hso(user)
