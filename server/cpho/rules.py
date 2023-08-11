from server.rules_framework import add_rule, auto_rule


@auto_rule
def is_admin(user):
    return user.username == "admin"


@auto_rule
def is_hso(user):
    return user.username == "hso"


@auto_rule
def is_admin_or_hso(user):
    return is_admin(user) or is_hso(user)


@auto_rule
def is_program(user):
    return (not is_admin_or_hso(user)) and user.phac_org_roles.exists()


@auto_rule
def is_branch_lead(user):
    return user.phac_org_roles.filter(is_phac_org_lead=True).exists()


@auto_rule
def is_branch_user(user):
    return not is_branch_lead(user)


@auto_rule
def is_branch_lead_or_user(user):
    return is_branch_user(user) or is_branch_lead(user)


# TODO: REMOVE THIS
@auto_rule
def is_indicator_lead(user, indicator):
    return True


# TODO: Check THIS
@auto_rule
def indicator_of_users_branch(user, indicator):
    # print(indicator.PHACOrg)
    # for phac_org_role in user.phac_org_roles.all():
    #     print(phac_org_role.phac_org)
    #     # if phac_org_role.phac_org == indicator.PHACOrg:
    # return True
    return user.phac_org_roles.filter(phac_org=indicator.PHACOrg).exists()


@auto_rule
def can_create_indicator(user):
    return is_admin_or_hso(user)


@auto_rule
def can_edit_indicator(user, indicator):
    # return (
    #     is_admin(user)
    #     or is_hso(user)
    #     or (is_program(user) and is_indicator_lead(user, indicator))
    #     or (
    #         is_program(user)
    #         and is_branch_lead(user)
    #         and indicator_of_users_branch(user, indicator)
    #     )
    # )
    return is_admin_or_hso(user)


@auto_rule
def can_edit_indicator_data(user, indicator):
    return is_admin_or_hso(user) or (
        indicator_of_users_branch(user, indicator) and is_branch_lead(user)
    )


@auto_rule
def can_view_indicator(user, indicator):
    return is_admin_or_hso(user) or indicator_of_users_branch(user, indicator)


@auto_rule
def can_view_indicator_data(user, indicator):
    # return can_view_indicator(user, indicator)
    return is_admin_or_hso(user) or indicator_of_users_branch(user, indicator)


@auto_rule
def can_submit_as_program(user, indicator):
    return (
        # is_admin(user)
        # or is_hso(user)
        # or (is_program(user) and is_indicator_lead(user, indicator))
        # or (
        #     is_program(user)
        #     and is_branch_lead(user)
        #     and indicator_of_users_branch(user, indicator)
        # )
        is_admin(user)
        or (
            indicator_of_users_branch(user, indicator) and is_branch_lead(user)
        )
    )


@auto_rule
def can_submit_as_hso(user, indicator):
    return is_admin_or_hso(user)


@auto_rule
def can_submit_as_hso_or_program(user, indicator):
    # return can_submit_as_hso(user, indicator) or can_submit_as_program(
    #     user, indicator
    # )
    return (
        is_admin(user)
        or (is_hso(user) and can_submit_as_hso(user, indicator))
        or (is_program(user) and can_submit_as_program(user, indicator))
    )
