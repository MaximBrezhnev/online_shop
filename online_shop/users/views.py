from django.contrib.auth import logout, authenticate, get_user_model, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.core.cache import cache
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, UpdateView

from online_shop.settings import USER_CONFIRMATION_KEY
from users import tasks
from users.forms import LoginForm, RegisterForm, ProfileForm, UserPasswordChangeForm
from users.tasks import send_email_with_link
from users.utils import create_link


def logout_view(request):
    logout(request)
    return redirect(to=reverse_lazy("users:login"))


class LoginView(View):
    def get(self, request):
        return render(
            request,
            "users/login.html",
            context={"form": LoginForm()}
        )

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_active is True:
                login(request, user)
                return redirect(
                    to=reverse_lazy("home")
                )

            form.add_error(None, "Invalid email or password")
            return render(
                request,
                "users/login.html",
                {"form": form},
            )


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:email_was_sent")
    
    def form_valid(self, form):
        user = get_user_model().objects.create(
            email=form.cleaned_data["email"],
            is_active=False
        )
        user.set_password(form.cleaned_data["password1"])
        user.save()

        confirm_link = create_link(self.request, user)
        # Синхронное тестирование
        send_email_with_link(confirm_link, user.email)
        # tasks.send_email_with_link.delay(confirm_link, user.email)

        return super().form_valid(form)


def register_confirm_view(request, token):
    redis_key = USER_CONFIRMATION_KEY.format(token=token)
    user_info = cache.get(redis_key) or {}
    user_id = user_info.get("user_id", None)

    if user_id is not None:
        user = get_object_or_404(get_user_model(), pk=user_id)
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        return redirect(to=reverse_lazy("home"))

    return redirect(to=reverse_lazy("home"))


def email_was_sent_view(request):
    return render(
        request,
        "users/email_was_sent.html"
    )


class ProfileView(UpdateView):
    pk_url_kwarg = "user_id"
    model = get_user_model()
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password_change_done')


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"




