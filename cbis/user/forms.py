from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)


class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=255, help_text="A random username will be generated if you leave this field blank")
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    username = forms.CharField(label="Username",
                               widget=forms.TextInput(attrs={'class': 'form-control input-lg'}))
    about_me = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control input-lg'}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if avatar and avatar.size > 1024 * 1024:
            raise ValidationError("Image file too large ( > 1mb )")
        else:
            return avatar

    class Meta:
        model = User
        fields = ["username", "about_me", "avatar"]
