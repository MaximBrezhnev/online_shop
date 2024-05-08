import uuid
from typing import Optional

from django.contrib.auth import authenticate, get_user_model, login
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from online_shop.settings import USER_CONFIRMATION_KEY, USER_CONFIRMATION_TIMEOUT
from users.forms import LoginForm


def _get_user_by_form_data(form: LoginForm, request: HttpRequest) -> get_user_model():
    email = form.cleaned_data.get("email")
    password = form.cleaned_data.get("password")
    return authenticate(request, email=email, password=password)


def _login(form: LoginForm, request: HttpRequest) -> bool:
    if form.is_valid():
        user = _get_user_by_form_data(form=form, request=request)
        if user is not None and user.is_active is True:
            login(request, user)
            return True
        form.add_error(None, "Неверный адрес электронной почты или пароль")
        return False


def _create_inactive_user(email: str, password: str) -> get_user_model():
    user = get_user_model().objects.create(
        email=email,
        is_active=False
    )
    user.set_password(password)
    user.save()
    return user


def _create_link(request: HttpRequest, user: get_user_model()) -> str:
    token = uuid.uuid4().hex
    redis_key = USER_CONFIRMATION_KEY.format(token=token)
    cache.set(
        redis_key,
        {"user_id": user.id},
        timeout=USER_CONFIRMATION_TIMEOUT,
    )

    confirm_link = request.build_absolute_uri(
        reverse_lazy(
            "users:register_confirm", kwargs={"token": token},
        )
    )

    return confirm_link


def _activate_user(user_id: str, request: HttpRequest) -> None:
    user = get_object_or_404(get_user_model(), pk=user_id)
    user.is_active = True
    user.save(update_fields=["is_active"])
    login(request, user)
