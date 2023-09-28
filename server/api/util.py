from collections import defaultdict

from pleasant_promises.dataloader import SingletonDataLoader


class GraphQLContext:
    def __init__(self, dataloaders, user):
        self.dataloaders = dataloaders
        self.user = user


class AbstractModelByIdLoader(SingletonDataLoader):
    model = None  # override this part

    @classmethod
    def batch_load(cls, ids):
        records = list(cls.model.objects.filter(id__in=ids))
        by_id = {record.id: record for record in records}
        return [by_id[id] for id in ids]


class PrimaryKeyDataLoaderFactory:
    """
    This ensures the same _class_ for a single model can only be created once.
    This is because some consumers dynamically create dataloaders based on models not yet known
    """

    dataloader_classes_by_model = {}

    @staticmethod
    def _create_dataloader_cls_for_model(model_cls):
        return type(
            f"{model_cls.__name__}ByIDLoader",
            (AbstractModelByIdLoader,),
            dict(model=model_cls),
        )

    @classmethod
    def get_model_by_id_loader(cls, model_cls):
        if model_cls in cls.dataloader_classes_by_model:
            return cls.dataloader_classes_by_model[model_cls]
        else:
            loader = cls._create_dataloader_cls_for_model(model_cls)
            cls.dataloader_classes_by_model[model_cls] = loader
            return loader


class AbstractChildModelByAttrLoader(SingletonDataLoader):
    """
    Loads many records by a single attr
    """

    model = None  # override this part
    attr = None  # override this part

    @classmethod
    def batch_load(cls, attr_values):
        records = list(
            cls.model.objects.filter(**{f"{cls.attr}__in": attr_values})
        )
        by_attr = defaultdict(list)
        for record in records:
            by_attr[getattr(record, cls.attr)].append(record)

        return [by_attr[attr_val] for attr_val in attr_values]
