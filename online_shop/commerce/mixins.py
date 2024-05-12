from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class DisplayMixin:
    def __str__(self):
        return self.__getattribute__("name")


class OrderedSearchMixin:
    def get_ordered_queryset(self, products):
        if self.request.GET.get("sort", None) == "price_desc":
            return products.order_by("-price")
        if self.request.GET.get("sort", None) == "price_asc":
            return products.order_by("price")
        return products


class WishlistLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("message_about_wishlist")
