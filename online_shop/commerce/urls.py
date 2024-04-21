from django.urls import path

from commerce import views

urlpatterns = [
    path("", views.IndexListView.as_view(), name="home"),
    path("<slug:product_slug>", views.ProductView.as_view(), name="product"),
]
