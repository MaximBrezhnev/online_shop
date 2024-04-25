from django.contrib.auth.views import LoginView
from django.views.generic import CreateView

from users.forms import LoginUserForm, RegisterUserForm


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = "users/login.html"


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "users/registration.html"
