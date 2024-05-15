from cart.forms import CheckoutForm
from cart.mixins import CartLoginRequiredMixin
from cart.services import _change_size_and_number
from cart.services import _change_size_and_number_when_increasing
from cart.services import _change_size_and_number_when_reducing
from cart.services import _create_order_items
from cart.services import _create_product_in_cart
from cart.services import _find_total_price
from cart.services import _find_total_quantity
from cart.services import _get_available_sizes
from cart.services import _get_products_in_cart_by_user
from cart.services import _remove_product
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import ListView


def add_to_cart_view(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    user_id = request.GET.get("user_id")
    product_id = request.GET.get("product_id")
    is_size = int(request.GET.get("is_size"))

    if is_size:
        sizes = _get_available_sizes(product_id=product_id, user_id=user_id)
        return render(
            request,
            "cart/choose_size.html",
            context={
                "product_id": product_id,
                "user_id": user_id,
                "sizes": sizes,
            },
        )

    _change_size_and_number(product_id)
    product_in_cart = _create_product_in_cart(
        product_id=product_id, user_id=user_id, number=1
    )
    return redirect(
        to=reverse("product", kwargs={"product_slug": product_in_cart.product.slug})
    )


def choose_size_view(request: HttpRequest) -> HttpResponseRedirect:
    user_id = request.GET.get("user_id")
    product_id = request.GET.get("product_id")
    size = request.GET.get("size")

    _change_size_and_number(product_id=product_id)
    product_in_cart = _create_product_in_cart(
        product_id=product_id, user_id=user_id, size=size, number=1
    )

    return redirect(
        to=reverse("product", kwargs={"product_slug": product_in_cart.product.slug})
    )


def remove_from_cart_view(request: HttpRequest) -> HttpResponseRedirect:
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    _remove_product(
        product_id=product_id,
        user_id=user_id,
        size=size,
    )
    return redirect(to=reverse("list_of_products_in_cart"))


class CartView(CartLoginRequiredMixin, ListView):
    template_name = "cart/cart.html"
    context_object_name = "products_in_cart"
    paginate_by = 3

    def get_queryset(self):
        return _get_products_in_cart_by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Корзина"
        return context


def message_about_cart_view(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "message_about_permission.html",
        context={"title": "Корзина недоступна", "section": "корзина"},
    )


def increase_view(request: HttpRequest) -> HttpResponseRedirect:
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    _change_size_and_number_when_increasing(
        product_id=product_id, user_id=user_id, size=size
    )

    return redirect(to=reverse("list_of_products_in_cart"))


def reduce_view(request: HttpRequest) -> HttpResponseRedirect:
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    _change_size_and_number_when_reducing(
        product_id=product_id, user_id=user_id, size=size
    )

    return redirect(to=reverse("list_of_products_in_cart"))


class CheckoutView(CreateView):
    form_class = CheckoutForm
    template_name = "cart/checkout.html"
    success_url = reverse_lazy("message_about_order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"

        object_list = _get_products_in_cart_by_user(self.request.user)
        context["total_price"] = _find_total_price(object_list)
        context["total_quantity"] = _find_total_quantity(object_list)

        return context

    def form_valid(self, form):
        order = form.save()
        _create_order_items(user=self.request.user, order=order)
        return super().form_valid(form)


def message_about_order_view(request: HttpRequest) -> HttpResponse:
    return render(
        request, "cart/message_about_order.html", context={"title": "Заказ оформлен"}
    )
