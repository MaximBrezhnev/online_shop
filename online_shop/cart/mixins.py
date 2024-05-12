from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy, reverse


class CartLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("message_about_cart")



