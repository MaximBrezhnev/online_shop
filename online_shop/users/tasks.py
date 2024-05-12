from smtplib import SMTPRecipientsRefused

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from online_shop.settings import DEFAULT_FROM_EMAIL, USER_CONFIRMATION_TIMEOUT


@shared_task
def send_email_with_link(confirm_link: str, email: str) -> None:
    try:
        send_mail(
            subject="Пожалуйста, подтвердите регистрацию",
            message=f"Перейдите, пожалуйста, по ссылке: "
                    f"{confirm_link}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[email, ]
        )
        _delete_inactive_user.apply_async(
            args=(email, ),
            countdown=USER_CONFIRMATION_TIMEOUT + 5
        )
    except SMTPRecipientsRefused:
        _delete_inactive_user(email=email)


@shared_task
def _delete_inactive_user(email: str) -> None:
    User = get_user_model()
    user = User.objects.get(email=email)
    if user.is_active is False:
        user.delete()









