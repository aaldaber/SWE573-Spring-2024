from django import forms
from .models import TemplateField, PostTemplate, Community


class CreateCommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ["name", "description", "is_public"]


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
            if each.data_type == "textarea":
                self.fields[field_name] = forms.CharField(required=each.required, widget=forms.Textarea(attrs={"rows":"5"}))
            elif each.data_type == "integer":
                self.fields[field_name] = forms.IntegerField(required=each.required)
            elif each.data_type == "boolean":
                self.fields[field_name] = forms.BooleanField(required=False)
            elif each.data_type == "float":
                self.fields[field_name] = forms.FloatField()
            elif each.data_type == "date":
                self.fields[field_name] = forms.DateField(input_formats=['%d-%m-%Y'], label="{} (DD-MM-YYYY)".format(field_name))
            elif each.data_type == "datetime":
                self.fields[field_name] = forms.DateTimeField()
            elif each.data_type == "file":
                self.fields[field_name] = forms.FileField()
            elif each.data_type == "image":
                self.fields[field_name] = forms.ImageField()
