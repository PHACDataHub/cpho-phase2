from django.utils.functional import cached_property
from django.views.generic import DetailView, ListView, TemplateView

from phac_aspc.rules import test_rule

from cpho.models import DimensionType, Indicator
from cpho.queries import (
    get_indicator_directories_for_user,
    get_indicators_for_user,
    get_metadata_submission_statuses,
    get_submission_statuses,
    relevant_dimension_types_for_period,
)
from cpho.util import group_by

from .view_util import (
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
    age_group_sort,
)


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"

    def get_queryset(self):
        if test_rule("is_admin_or_hso", self.request.user):
            return Indicator.objects.all().order_by("name")

        else:
            filtered = get_indicators_for_user(self.request.user.id)
            filtered = list(filtered)
            filtered.sort(key=lambda i: i.name)
            return filtered

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "user_indicator_directories": get_indicator_directories_for_user(
                self.request.user.id
            ),
        }


class ViewIndicator(MustPassAuthCheckMixin, TemplateView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"

    def check_rule(self):
        return test_rule(
            "can_access_indicator",
            self.request.user,
            self.indicator,
        )

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        indicator = Indicator.objects.get(pk=self.kwargs["pk"])
        relevant_periods = indicator.get_relevant_periods()

        all_data = indicator.data.filter(is_deleted=False).prefetch_related(
            "period"
        )
        periods_with_data = set(d.period for d in all_data)

        all_shown_periods = periods_with_data | set(relevant_periods)

        data_counts_by_period = {
            p: len([datum for datum in all_data if datum.period_id == p.id])
            for p in all_shown_periods
        }

        sorted_all_shown_periods = sorted(
            all_shown_periods, key=lambda p: ((-p.year), (p.quarter or -1))
        )

        submission_statuses_by_period = {
            p: get_submission_statuses(indicator, p) for p in all_shown_periods
        }

        alternate_periods = (
            set(indicator.get_adjacent_periods()) - periods_with_data
        )

        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
            "data_counts_by_period": data_counts_by_period,
            "indicator": indicator,
            "submission_statuses_by_period": submission_statuses_by_period,
            "metadata_submission_statuses": get_metadata_submission_statuses(
                indicator
            ),
            "alternate_periods": alternate_periods,
            "sorted_all_shown_periods": sorted_all_shown_periods,
        }


class ViewIndicatorForPeriod(
    MustPassAuthCheckMixin, SinglePeriodMixin, DetailView
):
    model = Indicator
    template_name = "indicators/view_indicator_for_period.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

    @cached_property
    def indicator_data(self):
        return (
            self.indicator.data.filter(period=self.period, is_deleted=False)
            .select_related("dimension_value")
            .prefetch_related("dimension_type")
            .with_submission_annotations()
            .with_last_version_date()
            .order_by("dimension_value")
        )

    @cached_property
    def indicator_data_by_dimension_type(self):
        data = group_by(
            list(self.indicator_data), lambda d: d.dimension_type_id
        )
        age_group_dim_id = DimensionType.objects.get(code="age").id
        age_data = data.get(age_group_dim_id, [])
        age_data = age_group_sort(age_data)
        data[age_group_dim_id] = age_data
        return data

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
            "dimension_types": relevant_dimension_types_for_period(
                self.indicator, self.period
            ),
            "submission_statuses": get_submission_statuses(
                self.indicator, self.period
            ),
            "indicator_data_by_dimension_type": self.indicator_data_by_dimension_type,
        }

    def check_rule(self):
        return test_rule(
            "can_access_indicator",
            self.request.user,
            self.indicator,
        )
