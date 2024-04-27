from django import forms
from .models import TemplateField, PostTemplate, Community


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ["name", "description", "is_public"]


class FieldForm(forms.ModelForm):
    class Meta:
        model = TemplateField
        fields = ["data_type", "label", "order", "required"]


class TemplateForm(forms.ModelForm):
    class Meta:
        model = PostTemplate
        fields = ["name"]


class TemplatePreviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields")
        super().__init__(*args, **kwargs)
        for each in fields:
            field_name = each.label
            if each.data_type == "text":
                self.fields[field_name] = forms.CharField(required=each.required)
            elif each.data_type == "integer":
                self.fields[field_name] = forms.IntegerField(required=each.required)
            elif each.data_type == "boolean":
                self.fields[field_name] = forms.BooleanField()
            elif each.data_type == "float":
                self.fields[field_name] = forms.FloatField()
            elif each.data_type == "date":
                self.fields[field_name] = forms.DateField()
            elif each.data_type == "datetime":
                self.fields[field_name] = forms.DateTimeField()
            elif each.data_type == "file":
                self.fields[field_name] = forms.FileField()
            elif each.data_type == "image":
                self.fields[field_name] = forms.ImageField()
