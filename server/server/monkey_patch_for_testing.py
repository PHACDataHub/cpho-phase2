from django.test import signals

from jinja2 import Template as Jinja2Template

# Sending a signal when templates get rendered allows us
# to access their context in tests
# useful for debugging and running assertions on forms
ORIGINAL_JINJA2_RENDERER = Jinja2Template.render


def instrumented_render(template_object, *args, **kwargs):
    context = dict(*args, **kwargs)
    signals.template_rendered.send(
        sender=template_object, template=template_object, context=context
    )
    return ORIGINAL_JINJA2_RENDERER(template_object, *args, **kwargs)


Jinja2Template.render = instrumented_render
