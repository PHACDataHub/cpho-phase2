import graphene
from graphene_django import DjangoObjectType
from .models import Indicator, Benchmarking, IndicatorData, TrendAnalysis


class IndicatorType(DjangoObjectType):
    class Meta:
        model = Indicator


class PossibleIndicatorResponseType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    category = graphene.String()
    data_point_count = graphene.Int()

    # def resolve_data_point_count(self, info, **kwargs):
    #     return IndicatorData.objects.filter(indicator=self).count()


class IndicatorDataType(DjangoObjectType):
    class Meta:
        model = IndicatorData


class BenchmarkingType(DjangoObjectType):
    class Meta:
        model = Benchmarking


class TrendAnalysisType(DjangoObjectType):
    class Meta:
        model = TrendAnalysis
        fields = (
            "id",
            "indicator",
            "detailed_indicator",
            "year",
            "data_point",
            "line_of_best_fit_point",
        )


# class CreateIndicator(graphene.Mutation):
#     class Arguments:
#         category = graphene.String(required=True)
#         topic = graphene.String(required=True)
#         indicator = graphene.String(required=True)
#         detailed_indicator = graphene.String(required=True)
#         sub_indicator_measurement = graphene.String()


class Query(graphene.ObjectType):
    indicators = graphene.List(IndicatorType)
    indicator_data = graphene.List(IndicatorDataType)
    possible_indicators = graphene.List(PossibleIndicatorResponseType)

    def resolve_indicators(root, info, **kwargs):
        # Querying a list
        return Indicator.objects.all()

    def resolve_indicator_data(root, info, **kwargs):
        # Querying a list
        return IndicatorData.objects.all()

    def resolve_possible_indicators(root, info, **kwargs):
        # indicators = Indicator.objects.all().values()
        response = []
        for ind in Indicator.objects.all():
            response.append(
                PossibleIndicatorResponseType(
                    id=ind.id,
                    name=ind.indicator,
                    category=ind.category,
                    data_point_count=IndicatorData.objects.filter(
                        indicator=ind.id
                    ).count(),
                )
            )
        return response


schema = graphene.Schema(query=Query)
