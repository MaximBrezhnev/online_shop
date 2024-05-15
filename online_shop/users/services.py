import uuid

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from users.forms import LoginForm

from online_shop.settings import USER_CONFIRMATION_KEY
from online_shop.settings import USER_CONFIRMATION_TIMEOUT


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
    user = get_user_model().objects.create(email=email, is_active=False)
    user.set_password(password)
    user.save()
    return user


def _create_cache_entry(user: get_user_model()) -> str:
    token = uuid.uuid4().hex
    redis_key = USER_CONFIRMATION_KEY.format(token=token)
    cache.set(
        redis_key,
        {"user_id": user.id},
        timeout=USER_CONFIRMATION_TIMEOUT,
    )
    return token


def _create_link(request: HttpRequest, user: get_user_model()) -> str:
    token = _create_cache_entry(user=user)

    confirm_link = request.build_absolute_uri(
        reverse(
            "users:register_confirm",
            kwargs={"token": token},
        )
    )

    return confirm_link


def _activate_user(user_id: str, request: HttpRequest) -> None:
    user = get_object_or_404(get_user_model(), pk=user_id)
    user.is_active = True
    user.save(update_fields=["is_active"])
    login(request, user)
