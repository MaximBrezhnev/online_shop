from django.urls import path

from commerce import views

urlpatterns = [
    path(
        "",
        views.IndexListView.as_view(),
        name="home"
    ),
    path(
        "<slug:product_slug>/",
        views.ProductView.as_view(),
        name="product"
    ),
    path(
        "categories/<slug:category_slug>/",
        views.ProductsByCategoryView.as_view(),
        name="products_by_category",
    ),
    path(
        "categories/<slug:category_slug>/<slug:subcategory_slug>/",
        views.ProductsBySubcategoryView.as_view(),
        name="products_by_subcategory"
    ),
    path(
        "search",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "search/products/",
        views.ProductsBySearchView.as_view(),
        name="products_by_search"
    )
]
