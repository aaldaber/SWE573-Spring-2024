from django import forms
from .models import PostTemplate, Community
from django.core.exceptions import ValidationError
from leaflet.forms.widgets import LeafletWidget
from leaflet.forms.fields import PointField


class CreateCommunityForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Community name", widget=forms.TextInput(attrs={'class': 'form-control input-lg', 'placeholder': '90s Music'}))
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control input-lg'}))
    picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if picture and picture.size > 1024 * 1024:
            raise ValidationError("Image file too large ( > 1mb )")
        else:
            return picture

    class Meta:
        model = Community
        fields = ["name", "description", "picture", "is_public"]


class TemplateForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Template name",
                           widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))

    class Meta:
        model = PostTemplate
        fields = ["name"]


class PostForm(forms.Form):
    post_title = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))


class TemplatePreviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields")
        super().__init__(*args, **kwargs)
        for each in fields:
            field_name = each.label
            if each.data_type == "text":
                self.fields[field_name] = forms.CharField(required=each.required, widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))
            if each.data_type == "textarea":
                self.fields[field_name] = forms.CharField(required=each.required, widget=forms.Textarea(attrs={'class': 'form-control input-lg', "rows":"5"}))
            elif each.data_type == "integer":
                self.fields[field_name] = forms.IntegerField(required=each.required, widget=forms.NumberInput(attrs={'class': 'form-control input-lg'}))
            elif each.data_type == "boolean":
                self.fields[field_name] = forms.BooleanField(required=False)
            elif each.data_type == "float":
                self.fields[field_name] = forms.FloatField(required=each.required, widget=forms.NumberInput(attrs={'class': 'form-control input-lg'}))
            elif each.data_type == "date":
                self.fields[field_name] = forms.DateField(required=each.required, input_formats=['%Y-%m-%d'], widget=forms.DateInput(attrs={'class': 'form-control input-lg', 'type': 'date'}))
            elif each.data_type == "datetime":
                self.fields[field_name] = forms.DateTimeField(required=each.required, input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'class': 'form-control input-lg', 'type': 'datetime-local'}))
            elif each.data_type == "file":
                self.fields[field_name] = forms.FileField(required=each.required, widget=forms.FileInput(attrs={'class': 'form-control'}))
            elif each.data_type == "image":
                self.fields[field_name] = forms.ImageField(required=each.required, widget=forms.FileInput(attrs={'class': 'form-control'}))
            elif each.data_type == "geolocation":
                self.fields[field_name] = PointField(required=each.required, widget=LeafletWidget())


class TemplateSearchForm(forms.Form):
    post_title = forms.CharField(max_length=255, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields")
        super().__init__(*args, **kwargs)
        for each in fields:
            field_name = each.label
            if each.data_type == "text":
                self.fields[field_name] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))
            if each.data_type == "textarea":
                self.fields[field_name] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))
            elif each.data_type == "integer":
                self.fields[field_name+"_from"] = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control input-lg'}))
                self.fields[field_name + "_to"] = forms.IntegerField(required=False, widget=forms.NumberInput(
                    attrs={'class': 'form-control input-lg'}))
            elif each.data_type == "boolean":
                self.fields[field_name] = forms.BooleanField(required=False)
            elif each.data_type == "float":
                self.fields[field_name+"_from"] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control input-lg'}))
                self.fields[field_name + "_to"] = forms.FloatField(required=False, widget=forms.NumberInput(
                    attrs={'class': 'form-control input-lg'}))
            elif each.data_type == "date":
                self.fields[field_name+"_from"] = forms.DateField(required=False, input_formats=['%Y-%m-%d'], widget=forms.DateInput(attrs={'class': 'form-control input-lg', 'type': 'date'}))
                self.fields[field_name + "_to"] = forms.DateField(required=False, input_formats=['%Y-%m-%d'],
                                                                    widget=forms.DateInput(
                                                                        attrs={'class': 'form-control input-lg',
                                                                               'type': 'date'}))
            elif each.data_type == "datetime":
                self.fields[field_name+"_from"] = forms.DateTimeField(required=False, input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'class': 'form-control input-lg', 'type': 'datetime-local'}))
                self.fields[field_name + "_to"] = forms.DateTimeField(required=False,
                                                                        input_formats=['%Y-%m-%dT%H:%M'],
                                                                        widget=forms.DateTimeInput(
                                                                            attrs={'class': 'form-control input-lg',
                                                                                   'type': 'datetime-local'}))