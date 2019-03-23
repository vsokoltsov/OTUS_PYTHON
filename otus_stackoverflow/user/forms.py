from django import forms
from .models import User
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate


class SignUpForm(forms.Form):
    """Create new user."""

    email = forms.EmailField(max_length=255, required=True)
    login = forms.CharField(max_length=255, strip=True, required=True)
    password = forms.CharField(
        max_length=255, min_length=6, required=True
    )
    password_confirmation = forms.CharField(
        max_length=255, min_length=6, required=True
    )

    def clean(self):
        """Clean data and add perform custom validation."""

        cleaned_data = super(SignUpForm, self).clean()

        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation:
            if password != password_confirmation:
                self.add_error(
                    'password_confirmation',
                    'Does not match password')
                raise forms.ValidationError("Does not match password")
        return cleaned_data

    def submit(self):
        """Submit the form. Create new user in case of success validation."""

        if not self.is_valid():
            return False

        try:
            with transaction.atomic():
                cleaned_data = self.cleaned_data
                self.object = User(
                    email=cleaned_data.get('email'),
                    login=cleaned_data.get('login')
                )
                self.object.set_password(cleaned_data.get('password'))
                self.object.save()
                return True
        except IntegrityError:
            self.add_error('email', 'Already present')
            return False


class SignInForm(forms.Form):
    """Sign in form class."""

    login = forms.CharField(max_length=255, strip=True, required=True)
    password = forms.CharField(
        max_length=255, min_length=6, required=True
    )

    def submit(self):
        """Submit the form. Get user by the data."""

        if not self.is_valid():
            return False

        cleaned_data = self.cleaned_data
        user = authenticate(
            username=cleaned_data.get('login'),
            password=cleaned_data.get('password')
        )

        if user:
            self.object = user
            return True
        else:
            self.errors['user'] = ['Does not exist']
            return False


class ProfileEditForm(forms.ModelForm):
    """Update's user information."""

    class Meta:
        """Form's metaclass."""

        model = User
        fields = [
            'email',
            'avatar'
        ]

    email = forms.EmailField(max_length=255, required=True)
    avatar = forms.FileField(required=False)

    def submit(self):
        """Submit the form. Get user by the data."""

        if not self.is_valid():
            return False

        try:
            cleaned_data = self.cleaned_data
            self.instance.email = cleaned_data.get('email')
            self.instance.avatar = cleaned_data.get('avatar')
            self.instance.save()

            return True
        except Exception as e:
            return False
