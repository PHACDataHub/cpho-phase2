import graphene
from graphene_django import DjangoObjectType
from .models import Indicator, Benchmarking, IndicatorData, TrendAnalysis
from graphene_django.rest_framework.serializer_converter import convert_serializer_to_input_type
from rest_framework import serializers

# DjangoObjectTypes

class IndicatorType(DjangoObjectType):
    class Meta:
        model = Indicator
        
class IndicatorDataType(DjangoObjectType):
    class Meta:
        model = IndicatorData

# Custom Responses

class PossibleIndicatorResponseType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    category = graphene.String()
    data_point_count = graphene.Int()

# Complex Types to use as Mutation argument
        
class DataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorData
        exclude = ('id','indicator')
        
class DataPointArgsInput(convert_serializer_to_input_type(DataPointSerializer)):
    pass

# Queries

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

# Mutations

class CreateIndicator(graphene.Mutation):
    class Arguments:
        category = graphene.String(required=True)
        topic = graphene.String(required=True)
        indicator = graphene.String(required=True)
        detailed_indicator = graphene.String(required=True)
        sub_indicator_measurement = graphene.String()
        data_points = graphene.List(DataPointArgsInput, required=True)
        
    indicator = graphene.Field(IndicatorType)
    dataPoints = graphene.List(IndicatorDataType)
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        points = kwargs.pop('data_points')
        indicator = Indicator.objects.create(**kwargs)
        indicator.save()
        
        dataPoints = []
        for point in points:
            p = IndicatorData.objects.create(
                indicator=indicator,
                **point
            )
            dataPoints.append(p)
            p.save()

        return CreateIndicator(indicator=indicator, dataPoints=dataPoints)


class Mutation(graphene.ObjectType):
    create_indicator = CreateIndicator.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
