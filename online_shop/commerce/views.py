import phonenumbers
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, FormView, CreateView

from commerce.forms import SearchForm, CheckoutForm
from commerce.models import Product, Subcategory, FavoriteProduct, ProductInCart, OrderItem, Category


class OrderedSearchMixin:
    def get_ordered_queryset(self, products):
        if self.request.GET.get("sort", None) == "price_desc":
            return products.order_by("-price")
        if self.request.GET.get("sort", None) == "price_asc":
            return products.order_by("price")
        return products


class IndexListView(ListView):
    template_name = "commerce/list_of_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return Product.in_stock.all()[:21]

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
        context["title"] = self.object

        if all(
                item.size == "" for item in
                self.object.size_and_number_set.all()
        ):
            context["is_size"] = 0
        else:
            context["is_size"] = 1

        user = self.request.user
        if not user.is_anonymous:
            if self.object in [p.product for p in user.favoriteproduct_set.all()]:
                context["is_favorite"] = 1

        context["in_cart"] = 0
        if not context["is_size"]:
            context["not_all_sizes_in_cart"] = 1
            try:
                ProductInCart.objects.get(
                    product_id=self.object.id,
                    user_id=user.id
                )
                context["in_cart"] = 1
            except:
                pass

        else:
            context["not_all_sizes_in_cart"] = 0
            for item in self.object.size_and_number_set.all():
                if item.number > 0:
                    try:
                        ProductInCart.objects.get(
                            product_id=item.product_id,
                            user_id=user.id,
                            size=item.size
                        )
                    except:
                        context["not_all_sizes_in_cart"] = 1
                        break

        return context


class ProductsByCategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/categories.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        products = Product.in_stock.filter(category__slug=self.kwargs["category_slug"])
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = Category.objects.get(slug=self.kwargs["category_slug"])
        context["cat_selected"] = self.kwargs["category_slug"]
        context["subcategories"] = Subcategory.objects.all()
        return context


class ProductsBySubcategoryView(OrderedSearchMixin, ListView):
    template_name = "commerce/subcategories.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        products = Product.in_stock.filter(
            category__slug=self.kwargs["category_slug"],
            subcategory__slug=self.kwargs["subcategory_slug"]
        )
        return super().get_ordered_queryset(products)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (f'{Category.objects.get(slug=self.kwargs["category_slug"])}: '
                            f'{str(Subcategory.objects.get(slug=self.kwargs["subcategory_slug"])).lower()}')
        context["cat_selected"] = self.kwargs["category_slug"]
        context["subcategory_selected"] = self.kwargs["subcategory_slug"]
        context["subcategories"] = Subcategory.objects.all()
        return context


class SearchView(FormView):
    template_name = "commerce/search.html"
    form_class = SearchForm
    success_url = reverse_lazy("products_by_search")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Поиск"
        previous_page = self.request.META.get("HTTP_REFERER")
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
        return context


def add_to_wishlist_view(request, product_id, user_id):
    favorite_product = FavoriteProduct.objects.create(
        product_id=product_id,
        user_id=user_id,
    )
    return redirect(
        to=reverse(
            "product",
            kwargs={"product_slug": favorite_product.product.slug}
        ),
    )


def remove_from_wishlist_view(request, product_id, user_id):
    removed_product = FavoriteProduct.objects.get(
        product_id=product_id,
        user_id=user_id
    )
    removed_product.delete()

    return redirect(
        to=reverse(
            "product",
            kwargs={"product_slug": removed_product.product.slug}
        ),
    )


def message_about_wishlist_view(request):
    return render(
        request,
        "commerce/message_about_permission.html",
        context={
            "title": "Избранное недоступно",
            "section": "избранное"
        }
    )


class FavoriteProductsView(ListView):
    template_name = "commerce/list_of_products.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        favorite_products_ids = [p.product_id for p in self.request.user.favoriteproduct_set.all()]
        return Product.in_stock.filter(pk__in=favorite_products_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Избранное"
        context["header"] = "Избранное"
        context["message"] = ("Учтите, что "
                              "товары, которых в данный момент нет в наличии, "
                              "не отображаются в избранном")
        return context


def add_to_cart_view(request):
    user_id = request.GET.get("user_id")
    product_id = request.GET.get("product_id")
    is_size = int(request.GET.get("is_size"))
    product = Product.in_stock.get(pk=product_id)

    if is_size:
        sizes = []
        for item in product.size_and_number_set.all():
            if item.number > 0:
                try:
                    ProductInCart.objects.get(
                        product_id=product_id,
                        user_id=user_id,
                        size=item.size,
                    )
                except:
                    sizes.append(item.size)

        return render(
            request,
            "commerce/choose_size.html",
            context={
                "product_id": product_id,
                "user_id": user_id,
                "sizes": sizes,
            }
        )

    size_and_number = product.size_and_number_set.all()[0]
    size_and_number.number -= 1
    size_and_number.save()

    ProductInCart.objects.create(
        product_id=product_id,
        user_id=user_id,
        number=1,
    )
    return redirect(
        to=reverse(
            "product",
            kwargs={"product_slug": product.slug}
        )
    )


def choose_size_view(request):
    user_id = request.GET.get("user_id")
    product_id = request.GET.get("product_id")
    size = request.GET.get("size")

    ProductInCart.objects.create(
        product_id=product_id,
        user_id=user_id,
        size=size,
        number=1
    )

    product = Product.objects.get(pk=product_id)
    size_and_number = product.size_and_number_set.get(size=size)
    size_and_number.number -= 1
    size_and_number.save()

    return redirect(
        to=reverse(
            "product",
            kwargs={"product_slug": product.slug}
        )
    )


def remove_from_cart_view(request):
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    if size is None:
        removed_product = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id
        )
        size_and_number = removed_product.product.size_and_number_set.all()[0]

    else:
        removed_product = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id,
            size=size,
        )
        size_and_number = removed_product.product.size_and_number_set.get(
            size=size
        )

    size_and_number.number += removed_product.number
    size_and_number.save()
    removed_product.delete()

    return redirect(
        to=reverse("list_of_products_in_cart")
    )


class CartView(ListView):
    template_name = "commerce/cart.html"
    context_object_name = "products_in_cart"
    paginate_by = 3

    def get_queryset(self):
        return ProductInCart.objects.filter(
            user_id=self.request.user.id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Корзина"
        return context


def message_about_cart_view(request):
    return render(
        request,
        "commerce/message_about_permission.html",
        context={
            "title": "Корзина недоступна",
            "section": "корзина"
        }
    )


def increase_view(request):
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    if size is None:
        product_in_cart = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id,
        )
        size_and_number = (Product.objects.get(pk=product_id).
                           size_and_number_set.get(product_id=product_id))
    else:
        product_in_cart = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id,
            size=size
        )
        size_and_number = (
            Product.objects.get(pk=product_id).
            size_and_number_set.get(
                product_id=product_id,
                size=size
            )
        )

    if size_and_number.number > 0:
        size_and_number.number -= 1
        size_and_number.save()
        product_in_cart.number += 1
        product_in_cart.save()

    return redirect(to=reverse("list_of_products_in_cart"))


def reduce_view(request):
    product_id = request.GET.get("product_id")
    user_id = request.GET.get("user_id")
    size = request.GET.get("size", None)

    if size is None:
        product_in_cart = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id,
        )
        size_and_number = (Product.objects.get(pk=product_id).
                           size_and_number_set.get(product_id=product_id))
    else:
        product_in_cart = ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id,
            size=size
        )
        size_and_number = (
            Product.objects.get(pk=product_id).
            size_and_number_set.get(
                product_id=product_id,
                size=size
            )
        )

    if product_in_cart.number > 1:
        size_and_number.number += 1
        size_and_number.save()
        product_in_cart.number -= 1
        product_in_cart.save()

    return redirect(to=reverse("list_of_products_in_cart"))


class CheckoutView(CreateView):
    form_class = CheckoutForm
    template_name = "commerce/checkout.html"
    success_url = reverse_lazy("message_about_order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Оформление заказа"
        object_list = ProductInCart.objects.filter(user_id=self.request.user.id)
        context["total_price"] = sum(p.product.price * p.number for p in object_list)
        context["total_quantity"] = sum(p.number for p in object_list)
        return context

    def form_valid(self, form):
        order = form.save()
        products_in_cart = ProductInCart.objects.filter(user=self.request.user)

        for p in products_in_cart:
            order_item = OrderItem.objects.create(
                product=p.product,
                number=p.number,
                order=order
            )
            if p.size:
                order_item.size = p.size
                order_item.save()
            p.delete()

        return super().form_valid(form)


def message_about_order_view(request):
    return render(
        request,
        "commerce/message_about_order.html",
        context={
            "title": "Заказ оформлен"
        }
    )
