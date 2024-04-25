from django.urls import path

from users import views


app_name = "users"

urlpatterns = [
    path("login", views.LoginUserView.as_view(), name="login"),
    path("registration", views.RegisterUserView.as_view(), name='registration')
]
