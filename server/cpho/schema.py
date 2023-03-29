import csv
from io import TextIOWrapper
from django.core.files.temp import NamedTemporaryFile
import graphene
from graphene_django import DjangoObjectType
from .models import ExportedFile, Indicator, Benchmarking, IndicatorData, TrendAnalysis
from graphene_django.rest_framework.serializer_converter import convert_serializer_to_input_type
from rest_framework import serializers
from graphene_file_upload.scalars import Upload

# DjangoObjectTypes

class IndicatorType(DjangoObjectType):
    class Meta:
        model = Indicator
        
class IndicatorDataType(DjangoObjectType):
    class Meta:
        model = IndicatorData

class ExportedFileType(DjangoObjectType):
    class Meta:
        model = ExportedFile

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
    indicator = graphene.Field(IndicatorType, id=graphene.Int())
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

    def resolve_indicator(root, info, **kwargs):
        # Querying a single object
        id = kwargs.get('id')
        if id is not None:
            return Indicator.objects.get(pk=id)
        return None

# Mutations

class ImportDataMutation(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, file):
        reader = csv.reader(TextIOWrapper(file, encoding="utf8"), delimiter=',')
        print(reader)
        rowCount = 0
        for row in reader:
            if rowCount != 0 and row != []:
                print("ROW")
                print(row)
                ind = Indicator.objects.update_or_create(
                    category = row[0],
                    topic = row[1],
                    indicator = row[2],
                    detailed_indicator = row[3],
                    sub_indicator_measurement = row[4],
                )
                IndicatorData.objects.update_or_create(
                    indicator = ind[0],
                    country = row[5],
                    geography = row[6],
                    sex = row[7],
                    gender = row[8],
                    age_group = row[9],
                    age_group_type = row[10],
                    data_quality = row[11],
                    value = row[12].replace('<', ''),
                    value_lower_bound = row[13] if row[13] != '' else None,
                    value_upper_bound = row[14] if row[14] != '' else None,
                    value_unit = row[15],
                    single_year_timeframe = row[16],
                    multi_year_timeframe = row[17],
                )
            rowCount += 1
        print("DONE!!")

        return ImportDataMutation(success=True)

class ExportDataMutation(graphene.Mutation):
    class Arguments:
        selected_indicators = graphene.List(graphene.Int, required=True)

    csv_file = graphene.Field(lambda: ExportedFileType)

    @classmethod
    def mutate(cls, root, info, selected_indicators):
        temp_file = NamedTemporaryFile(delete=False)

        with open(temp_file.name, 'w') as f:
            fieldnames = ['category',
                  'topic',
                  'indicator',
                  'detailed_indicator',
                  'sub_indicator_measurement',
                  'country',
                  'geography',
                  'sex',
                  'gender',
                  'age_group',
                  'age_group_type',
                  'data_quality',
                  'value',
                  'value_lower_bound',
                  'value_upper_bound',
                  'value_unit',
                  'single_year_timeframe',
                  'multi_year_timeframe',
                  ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for id in selected_indicators:
                indicator = Indicator.objects.get(pk=id)
                points = IndicatorData.objects.filter(indicator=indicator)
                for point in points:
                    writer.writerow({
                    'category': indicator.category,
                    'topic': indicator.topic,
                    'indicator': indicator.indicator,
                    'detailed_indicator': indicator.detailed_indicator,
                    'sub_indicator_measurement': indicator.sub_indicator_measurement,
                    'country': point.country,
                    'geography': point.geography,
                    'sex': point.sex,
                    'gender': point.gender,
                    'age_group': point.age_group,
                    'age_group_type': point.age_group_type,
                    'data_quality': point.data_quality,
                    'value': point.value,
                    'value_lower_bound': point.value_lower_bound,
                    'value_upper_bound': point.value_upper_bound,
                    'value_unit': point.value_unit,
                    'single_year_timeframe': point.single_year_timeframe,
                    'multi_year_timeframe': point.multi_year_timeframe
                    })

        return ExportDataMutation(csv_file=temp_file.name)

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

class ModifyIndicator(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        category = graphene.String(required=True)
        topic = graphene.String(required=True)
        indicator = graphene.String(required=True)
        detailedIndicator = graphene.String(required=True)
        subIndicatorMeasurement = graphene.String()
        dataPoints = graphene.List(DataPointArgsInput, required=True)
        
        
    success = graphene.Boolean()
    indicator = graphene.Field(IndicatorType)
    dataPoints = graphene.List(IndicatorDataType)
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        points = kwargs.pop('dataPoints')
        id = kwargs.pop('id')
        category = kwargs.pop('category')
        topic = kwargs.pop('topic')
        indicatorName = kwargs.pop('indicator')
        detailedIndicator = kwargs.pop('detailedIndicator')
        subIndicatorMeasurement = kwargs.pop('subIndicatorMeasurement')

        try:
            indicatorObj = Indicator.objects.get(id=id)
            indicatorObj.category = category
            indicatorObj.topic = topic
            indicatorObj.indicator = indicatorName
            indicatorObj.detailed_indicator = detailedIndicator
            indicatorObj.sub_indicator_measurement = subIndicatorMeasurement    
            indicatorObj.save()

            dataPoints = []
            pastPoints = IndicatorData.objects.filter(indicator_id=id)
            pastPoints.delete()
            for point in points:
                p = IndicatorData.objects.create(
                    indicator=indicatorObj,
                    **point
                )
                p.save()
                dataPoints.append(p)

            return ModifyIndicator(indicator=indicatorObj, dataPoints=dataPoints, success=True)

        except Indicator.DoesNotExist:

            print("Could not find")
            return ModifyIndicator(indicator=None, dataPoints=None, success=False)

        except Exception as e:
            print(e)
            return ModifyIndicator(indicator=None, dataPoints=None, success=False)

class Mutation(graphene.ObjectType):
    create_indicator = CreateIndicator.Field()
    modify_indicator = ModifyIndicator.Field()
    import_data = ImportDataMutation.Field()
    export_data = ExportDataMutation.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)
