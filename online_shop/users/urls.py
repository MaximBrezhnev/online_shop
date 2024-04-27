from django.urls import path

from users import views


app_name = "users"

urlpatterns = [
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registration", views.RegisterView.as_view(), name='registration'),
    path(
        "registration/registration-confirmation/<str:token>",
        views.register_confirm_view,
        name="register_confirm"
    ),
    path(
        "registration/email-was-sent",
        views.email_was_sent_view,
        name="email_was_sent",
    )
]
