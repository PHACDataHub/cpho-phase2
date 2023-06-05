from django import apps
from django.contrib import admin

# Register your models here.
this_app = apps.registry.apps.all_models["cpho"]

for model in this_app.values():
    if hasattr(model, "__add_to_admin"):
        admin.site.register(model)
