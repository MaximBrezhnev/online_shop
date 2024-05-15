from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordChangeView
from django.core.cache import cache
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.views.generic import UpdateView
from users import tasks
from users.forms import LoginForm
from users.forms import ProfileForm
from users.forms import RegisterForm
from users.forms import UserPasswordChangeForm
from users.mixins import ProfileLoginRequiredMixin
from users.services import _activate_user
from users.services import _create_inactive_user
from users.services import _create_link
from users.services import _login

from online_shop.settings import USER_CONFIRMATION_KEY


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect(to=reverse("users:login"))


class LoginView(View):
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        return render(
            request, "users/login.html", context={"title": "Вход", "form": LoginForm()}
        )

    def post(self, request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        form = LoginForm(request.POST)

        if _login(form, request):
            return redirect(to=reverse("home"))
        return render(
            request,
            "users/login.html",
            context={"title": "Вход", "form": form},
        )


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:email_was_sent")
    extra_context = {"title": "Регистрация"}

    def form_valid(self, form):
        user = _create_inactive_user(
            email=form.cleaned_data["email"], password=form.cleaned_data["password1"]
        )

        confirm_link = _create_link(self.request, user)
        tasks.send_email_with_link.delay(confirm_link, user.email)
        return super().form_valid(form)


def register_confirm_view(request: HttpRequest, token: str) -> HttpResponseRedirect:
    redis_key = USER_CONFIRMATION_KEY.format(token=token)
    user_info = cache.get(redis_key) or {}
    user_id = user_info.get("user_id", None)

    if user_id is None:
        return render(
            request,
            "users/invalid_link.html",
            context={"title": "Ссылка недействительна"},
        )

    _activate_user(request=request, user_id=user_id)
    return redirect(to=reverse("home"))


def email_was_sent_view(request: HttpRequest) -> HttpResponse:
    return render(
        request, "users/email_was_sent.html", context={"title": "Письмо отправлено"}
    )


class ProfileView(ProfileLoginRequiredMixin, UpdateView):
    pk_url_kwarg = "user_id"
    model = get_user_model()
    form_class = ProfileForm
    template_name = "users/profile.html"
    extra_context = {"title": "Профиль"}


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:password_change_done")
    extra_context = {"title": "Смена пароля"}


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"
    extra_context = {"title": "Пароль изменен"}
