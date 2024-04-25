from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User


class LoginUserForm(AuthenticationForm):
    email = forms.EmailField(
        label="Электронная почта"
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput()
    )

    field_order = ("email", "password", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')

    class Meta:
        model = get_user_model()
        fields = ("email", "password", )


class RegisterUserForm(UserCreationForm):
    # Добавить labels
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", )

