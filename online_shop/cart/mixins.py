from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class CartLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("message_about_cart")
