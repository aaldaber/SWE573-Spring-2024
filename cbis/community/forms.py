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
