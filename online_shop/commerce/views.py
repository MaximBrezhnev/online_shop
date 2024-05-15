from commerce.forms import SearchForm
from commerce.mixins import OrderedSearchMixin
from commerce.mixins import WishlistLoginRequiredMixin
from commerce.models import Product
from commerce.services import _create_product_in_wishlist
from commerce.services import _get_category_by_slug
from commerce.services import _get_current_sort
from commerce.services import _get_newest_products
from commerce.services import _get_products_by_category
from commerce.services import _get_products_by_category_and_subcategory
from commerce.services import _get_products_in_wishlist
from commerce.services import _get_subcategories
from commerce.services import _get_subcategory_by_slug
from commerce.services import _get_title_by_category_and_subcategory
from commerce.services import _in_cart_and_not_all_sizes_in_cart
from commerce.services import _is_favorite
from commerce.services import _is_size
from commerce.services import _remove_product_from_wishlist
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView


class IndexListView(ListView):
    template_name = "commerce/list_of_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return _get_newest_products()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = "Новинки"
        context["title"] = "Главная"
        return context


class ProductView(DetailView):
    slug_url_kwarg = "product_slug"
    template_name = "commerce/product.html"
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        user = self.request.user

        context["title"] = product.name
        context["is_size"] = _is_size(product=product)
        context["is_favorite"] = _is_favorite(product=product, user=user)
        (
            context["in_cart"],
            context["not_all_sizes_in_cart"],
        ) = _in_cart_and_not_all_sizes_in_cart(
            is_size=context["is_size"], product=product, user=user
        )

        return context


class ProductsByCategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/categories.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        products = _get_products_by_category(category_slug=self.kwargs["category_slug"])
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = _get_category_by_slug(slug=self.kwargs["category_slug"])
        context["title"] = category.name
        context["cat_selected"] = category
        context["subcategories"] = _get_subcategories()
        context["sort"] = _get_current_sort(request=self.request)
        return context


class ProductsBySubcategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/subcategories.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        products = _get_products_by_category_and_subcategory(
            category_slug=self.kwargs["category_slug"],
            subcategory_slug=self.kwargs["subcategory_slug"],
        )
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs["category_slug"]
        subcategory_slug = self.kwargs["subcategory_slug"]

        context["title"] = _get_title_by_category_and_subcategory(
            category_slug=category_slug, subcategory_slug=subcategory_slug
        )
        context["cat_selected"] = _get_category_by_slug(slug=category_slug)
        context["subcategory_selected"] = _get_subcategory_by_slug(
            slug=subcategory_slug
        )
        context["subcategories"] = _get_subcategories()
        context["sort"] = _get_current_sort(request=self.request)
        return context


class SearchView(FormView):
    template_name = "commerce/search.html"
    form_class = SearchForm
    success_url = reverse_lazy("products_by_search")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.META.get("HTTP_REFERER")
        context["title"] = "Поиск"
        context["previous_page"] = previous_page
        return context


class ProductsBySearchView(OrderedSearchMixin, ListView):
    template_name = "commerce/products_by_search.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get("query")
        products = Product.in_stock.filter(name__istartswith=query)
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Товары по запросу"
        context["current_query"] = self.request.GET.get("query")
        context["sort"] = _get_current_sort(request=self.request)
        return context


def add_to_wishlist_view(
    request: HttpRequest, product_id: str, user_id: str
) -> HttpResponseRedirect:
    favorite_product = _create_product_in_wishlist(
        product_id=product_id,
        user_id=user_id,
    )
    return redirect(
        to=reverse("product", kwargs={"product_slug": favorite_product.product.slug}),
    )


def remove_from_wishlist_view(
    request: HttpRequest, product_id: str, user_id: str
) -> HttpResponseRedirect:
    removed_product = _remove_product_from_wishlist(
        product_id=product_id, user_id=user_id
    )

    return redirect(
        to=reverse("product", kwargs={"product_slug": removed_product.product.slug}),
    )


def message_about_wishlist_view(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "message_about_permission.html",
        context={"title": "Избранное недоступно", "section": "избранное"},
    )


class FavoriteProductsView(WishlistLoginRequiredMixin, ListView):
    template_name = "commerce/list_of_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return _get_products_in_wishlist(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Избранное"
        context["header"] = "Избранное"
        context["message"] = (
            "Учтите, что "
            "товары, которых в данный момент нет в наличии, "
            "не отображаются в избранном"
        )
        return context
