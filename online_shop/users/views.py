import uuid

from django.contrib.auth import logout, authenticate, get_user_model, login
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from online_shop.settings import DEFAULT_FROM_EMAIL, USER_CONFIRMATION_KEY, USER_CONFIRMATION_TIMEOUT
from users.forms import LoginForm, RegisterForm


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
        user, created = get_user_model().objects.get_or_create(
            email=form.cleaned_data["email"],
            is_active=False
        )
        user.set_password(form.cleaned_data["password1"])
        user.save()

        if created:
            token = uuid.uuid4().hex
            redis_key = USER_CONFIRMATION_KEY.format(token=token)
            cache.set(
                redis_key,
                {"user_id": user.id},
                timeout=USER_CONFIRMATION_TIMEOUT,
            )

            confirm_link = self.request.build_absolute_uri(
                reverse_lazy(
                    "users:register_confirm", kwargs={"token": token},
                )
            )

            send_mail(
                subject="Пожалуйста, подтвердите регистрацию",
                message=f"Перейдите, пожалуйста, по ссылке: "
                        f"{confirm_link}",
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ]
            )

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




