import time
from datetime import datetime, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from online_shop.settings import DEFAULT_FROM_EMAIL, USER_CONFIRMATION_TIMEOUT


@shared_task
def send_email_with_link(confirm_link, email):
    send_mail(
        subject="Пожалуйста, подтвердите регистрацию",
        message=f"Перейдите, пожалуйста, по ссылке: "
                f"{confirm_link}",
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[email, ]
    )

    # Синхронное тестирование
    # time.sleep(10)
    # delete_inactive_user(email)

    # delete_inactive_user.subtask(
    #     args=(email, ),
    #     eta=datetime.now() + timedelta(seconds=USER_CONFIRMATION_TIMEOUT+10)
    # )


@shared_task
def delete_inactive_user(email):
    User = get_user_model()
    user = User.objects.get(email=email)
    if user.is_active is False:
        user.delete()







