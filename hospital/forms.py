from django import forms
from django.forms import modelform_factory


def hospital_form(model, fields):
    base_form = modelform_factory(model, fields=fields)

    class CustomForm(base_form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                if isinstance(field, forms.DateField):
                    field.widget = forms.DateInput(attrs={"type": "date", "class": "form-control"})
                elif isinstance(field, forms.DateTimeField):
                    field.widget = forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
                else:
                    existing_class = field.widget.attrs.get("class", "")
                    if "form-control" not in existing_class:
                        field.widget.attrs["class"] = f"{existing_class} form-control".strip()

    return CustomForm
