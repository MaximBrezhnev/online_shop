from cart import views
from django.urls import path

urlpatterns = [
    path(
        "list-of-products-in-cart/",
        views.CartView.as_view(),
        name="list_of_products_in_cart",
    ),
    path("add-to-cart/", views.add_to_cart_view, name="add_to_cart"),
    path("choose-size/", views.choose_size_view, name="choose_size"),
    path(
        "remove-from-cart/",
        views.remove_from_cart_view,
        name="remove_from_cart",
    ),
    path(
        "message-about-cart/", views.message_about_cart_view, name="message_about_cart"
    ),
    path(
        "increase/",
        views.increase_view,
        name="increase",
    ),
    path("reduce/", views.reduce_view, name="reduce"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path(
        "message-about-order/",
        views.message_about_order_view,
        name="message_about_order",
    ),
]
