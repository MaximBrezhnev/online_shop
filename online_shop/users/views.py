from django.contrib.auth import logout, authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.core.cache import cache
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, UpdateView

from online_shop.settings import USER_CONFIRMATION_KEY
from users import tasks
from users.forms import LoginForm, RegisterForm, ProfileForm, UserPasswordChangeForm
from users.mixins import CustomLoginRequiredMixin
from users.services import _login, _create_inactive_user, _create_link, _activate_user


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect(to=reverse("users:login"))


class LoginView(View):
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        return render(
            request,
            "users/login.html",
            context={
                "title": "Вход",
                "form": LoginForm()
            }
        )

    def post(self, request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        form = LoginForm(request.POST)

        if _login(form, request):
            return redirect(
                to=reverse("home")
            )
        return render(
            request,
            "users/login.html",
            context={
                "title": "Вход",
                "form": form
            },
        )


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:email_was_sent")
    extra_context = {
        "title": "Регистрация"
    }
    
    def form_valid(self, form):
        user = _create_inactive_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"]
        )

        confirm_link = _create_link(self.request, user)
        result_of_sending = tasks.send_email_with_link.delay(confirm_link, user.email)
        if result_of_sending is None:
            return super().form_valid(form)
        form.add_error("email", "Данный адрес электронной почты не существует")
        return render(
            self.request,
            "users/registration.html",
            context={
                "title": "Регистрация",
                "form": form
            }
        )


def register_confirm_view(request: HttpRequest, token: str) -> HttpResponseRedirect:
    redis_key = USER_CONFIRMATION_KEY.format(token=token)
    user_info = cache.get(redis_key) or {}
    user_id = user_info.get("user_id", None)

    if user_id is None:
        return render(
            request,
            "users/invalid_link.html",
            context={"title": "Ссылка недействительна"}
        )

    _activate_user(request=request, user_id=user_id)
    return redirect(to=reverse("home"))


def email_was_sent_view(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "users/email_was_sent.html",
        context={
            "title": "Письмо отправлено"
        }
    )


class ProfileView(CustomLoginRequiredMixin, UpdateView):
    pk_url_kwarg = "user_id"
    model = get_user_model()
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")
    extra_context = {
        "title": "Профиль"
    }


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password_change_done')
    extra_context = {
        "title": "Смена пароля"
    }


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"
    extra_context = {
        "title": "Пароль изменен"
    }




