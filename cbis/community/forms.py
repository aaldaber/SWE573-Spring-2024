from django import forms
from .models import PostTemplate, Community
from django.forms.utils import pretty_name


class CreateCommunityForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Community name", widget=forms.TextInput(attrs={'class': 'form-control input-lg', 'placeholder': '90s Music'}))
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control input-lg'}))

    class Meta:
        model = Community
        fields = ["name", "description", "is_public"]


class TemplateForm(forms.ModelForm):
    class Meta:
        model = PostTemplate
        fields = ["name"]


class PostForm(forms.Form):
    post_title = forms.CharField(max_length=255, required=True)


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
                self.fields[field_name] = forms.FloatField(required=each.required)
            elif each.data_type == "date":
                self.fields[field_name] = forms.DateField(required=each.required, input_formats=['%d-%m-%Y'], label="{} (DD-MM-YYYY)".format(pretty_name(field_name)))
            elif each.data_type == "datetime":
                self.fields[field_name] = forms.DateTimeField(required=each.required, input_formats=['%d-%m-%Y %H:%M'], label="{} (DD-MM-YYYY HH:MM)".format(pretty_name(field_name)))
            elif each.data_type == "file":
                self.fields[field_name] = forms.FileField(required=each.required)
            elif each.data_type == "image":
                self.fields[field_name] = forms.ImageField(required=each.required)
