import uuid

from django.core.cache import cache
from django.urls import reverse_lazy

from online_shop.settings import USER_CONFIRMATION_KEY, USER_CONFIRMATION_TIMEOUT


def create_link(request, user):
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
