import graphene
from graphene import List, NonNull

from cpho.models import Indicator as IndicatorModel

from .dataloaders import IndicatorByIdLoader
from .types import Indicator


class RootQuery(graphene.ObjectType):
    indicators = NonNull(List(NonNull(Indicator)))

    def resolve_indicators(self, info):
        return IndicatorModel.objects.all()

    indicator = graphene.Field(
        Indicator,
        id=graphene.Argument(NonNull(graphene.Int)),
    )

    def resolve_indicator(self, info, id):
        return IndicatorByIdLoader(info.context.dataloaders).load(id)


schema = graphene.Schema(query=RootQuery)
