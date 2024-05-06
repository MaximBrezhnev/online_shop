from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.forms import ModelForm


class LoginForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(),
    )


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("email", )
        labels = {
            "email": "Электронная почта"
        }


class ProfileForm(ModelForm):
    email = forms.CharField(
        disabled=True,
        required=False,
        label='Электронная почта',
    )

    class Meta:
        model = get_user_model()
        fields = ("email", )
        labels = {
            "email": "Электронная почта",
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Повтор пароля",
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))
