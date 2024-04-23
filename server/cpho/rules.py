from phac_aspc.rules import add_rule, auto_rule

from cpho.models import IndicatorDirectoryUserAccess
from cpho.queries import get_indicators_for_user


@auto_rule
def is_inputting_user(user):
    return len(get_indicators_for_user(user.id)) > 0


@auto_rule
def is_admin(user):
    return user.is_admin


@auto_rule
def is_hso(user):
    return user.is_hso


@auto_rule
def is_admin_or_hso(user):
    return is_admin(user) or is_hso(user)


@auto_rule
def can_access_indicator_directory(user, indicator_directory_id):
    if is_admin_or_hso(user):
        return True

    return IndicatorDirectoryUserAccess.objects.filter(
        user=user, directory_id=indicator_directory_id
    ).exists()


@auto_rule
def can_access_indicator(user, indicator):
    if is_admin_or_hso(user):
        return True

    allowed_indicators = get_indicators_for_user(user.id)
    return indicator in allowed_indicators


@auto_rule
def can_create_indicator(user):
    return is_admin_or_hso(user)


@auto_rule
def can_edit_indicator(user, indicator):
    # return is_admin_or_hso(user)
    return can_access_indicator(user, indicator)


@auto_rule
def can_edit_indicator_data(user, indicator):
    return can_access_indicator(user, indicator)


@auto_rule
def can_use_indicator_upload(user):
    return is_admin_or_hso(user) or is_inputting_user(user)


@auto_rule
def can_manage_users(user):
    return is_admin_or_hso(user)


@auto_rule
def can_submit_as_hso(user, indicator):
    return is_admin_or_hso(user)


@auto_rule
def can_submit_indicator(user, indicator):
    return can_access_indicator(user, indicator)


@auto_rule
def can_export_indicator(user, indicator):
    if indicator:
        return can_access_indicator(user, indicator)

    return can_use_indicator_upload(user)


@auto_rule
def can_export_benchmarking(user, indicator):
    # TODO: need to update this
    return is_admin_or_hso(user)


@auto_rule
def can_edit_benchmarking(user, indicator):
    return is_admin_or_hso(user)


@auto_rule
def can_view_benchmarking(user, indicator):
    return can_edit_benchmarking(user, indicator) or (
        is_inputting_user(user) and not is_admin_or_hso(user)
    )


@auto_rule
def can_edit_trend_analysis(user, indicator):
    return can_edit_indicator(user, indicator)
