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
        "search/form/",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "search/products/",
        views.ProductsBySearchView.as_view(),
        name="products_by_search"
    ),
    path(
        "wishlist/add-to-wishlist/<int:product_id>/<int:user_id>/",
        views.add_to_wishlist_view,
        name="add_to_wishlist",
    ),
    path(
        "wishlist/remove-form-wishlist/<int:product_id>/<int:user_id>/",
        views.remove_from_wishlist_view,
        name="remove_from_wishlist"
    ),
    path(
        "wishlist/message-about-wishlist/",
        views.message_about_wishlist_view,
        name="message_about_wishlist"
    ),
    path(
        "wishlist/list-of-favorite/",
        views.FavoriteProductsView.as_view(),
        name="list_of_favorite",
    ),
]
