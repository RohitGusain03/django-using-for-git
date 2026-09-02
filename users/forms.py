from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com"}
        )
    )

    class Meta:

        model = User

        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Create a password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm password"}
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class UserUpdateForm(forms.ModelForm):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:

        model = User

        fields = ["username", "email"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            "profile_image",
            "banner_image",
            "bio",
            "location",
            "website",
            "github",
            "linkedin",
        ]

        widgets = {

            "profile_image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),

            "banner_image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),

            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Tell us about yourself...",
                    "maxlength": 250,
                    "data-char-count": "bioCounter",
                }
            ),

            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your location"}
            ),

            "website": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com"}
            ),

            "github": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username",
                }
            ),

            "linkedin": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://linkedin.com/in/username",
                }
            ),
        }
