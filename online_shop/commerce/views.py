from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView

from commerce.forms import SearchForm
from commerce.models import Product, Subcategory


class OrderedSearchMixin:
    def get_ordered_queryset(self, products):
        if self.request.GET.get("sort", None) == "price_desc":
            return products.order_by("-price")
        if self.request.GET.get("sort", None) == "price_asc":
            return products.order_by("price")
        return products


class IndexListView(ListView):
    template_name = "commerce/index.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.in_stock.all()


class ProductView(DetailView):
    slug_url_kwarg = "product_slug"
    template_name = "commerce/product.html"
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if all(
            item.size == "" for item in
            context[self.context_object_name].size_and_number_set.all()
        ):
            context["is_size"] = False
        else:
            context["is_size"] = True

        return context


class ProductsByCategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/categories.html"
    context_object_name = "products"

    def get_queryset(self):
        products = Product.in_stock.filter(category__slug=self.kwargs["category_slug"])
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subcategories"] = Subcategory.objects.all()
        return context


class ProductsBySubcategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/subcategories.html"
    context_object_name = "products"

    def get_queryset(self):
        products = Product.in_stock.filter(
            category__slug=self.kwargs["category_slug"],
            subcategory__slug=self.kwargs["subcategory_slug"]
        )
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_selected"] = self.kwargs["category_slug"]
        context["subcategories"] = Subcategory.objects.all()
        return context


class SearchView(FormView):
    template_name = "commerce/search.html"
    form_class = SearchForm
    success_url = reverse_lazy("products_by_search")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page = self.request.META.get("HTTP_REFERER")
        context["previous_page"] = previous_page
        return context


class ProductsBySearchView(OrderedSearchMixin, ListView):
    template_name = "commerce/products_by_search.html"
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("query")
        products = Product.in_stock.filter(name__istartswith=query)
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_query"] = self.request.GET.get("query")
        return context










