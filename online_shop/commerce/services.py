from django.contrib.auth import get_user_model
from django.http import HttpRequest

from cart.models import ProductInCart
from commerce.models import Product, Category, Subcategory, FavoriteProduct


def _get_newest_products() -> list[Product]:
    return Product.in_stock.all()[:21]


def _is_size(product: Product) -> int:
    if all(
            item.size == "" for item in
            product.size_and_number_set.all()
    ):
        return 0
    return 1


def _is_favorite(product: Product, user: get_user_model()) -> int:
    if not user.is_anonymous:
        if product in [p.product for p in user.favoriteproduct_set.all()]:
            return 1
    return 0


def _in_cart_and_not_all_sizes_in_cart(
        is_size: int,
        product: Product,
        user: get_user_model()
) -> tuple[int, int]:
    in_cart = 0
    if not is_size:
        not_all_sizes_in_cart = 1
        try:
            ProductInCart.objects.get(
                product_id=product.pk,
                user_id=user.pk
            )
            in_cart = 1
        except ProductInCart.DoesNotExist:
            pass
    else:
        not_all_sizes_in_cart = 0
        for item in product.size_and_number_set.all():
            if item.number > 0:
                try:
                    ProductInCart.objects.get(
                        product_id=item.product_id,
                        user_id=user.id,
                        size=item.size
                    )
                except ProductInCart.DoesNotExist:
                    not_all_sizes_in_cart = 1
                    break

    return in_cart, not_all_sizes_in_cart


def _get_products_by_category(category_slug: str) -> list[Product]:
    return Product.in_stock.filter(category__slug=category_slug)


def _get_category_by_slug(slug: str) -> Category:
    return Category.objects.get(slug=slug)


def _get_subcategories() -> list[Subcategory]:
    return Subcategory.objects.all()


def _get_products_by_category_and_subcategory(
        category_slug: str,
        subcategory_slug: str
) -> list[Product]:
    return Product.in_stock.filter(
            category__slug=category_slug,
            subcategory__slug=subcategory_slug
    )


def _get_title_by_category_and_subcategory(
        category_slug: str,
        subcategory_slug: str
) -> str:
    return (f'{Category.objects.get(slug=category_slug)}: '
            f'{str(Subcategory.objects.get(slug=subcategory_slug)).lower()}')


def _get_subcategory_by_slug(slug: str) -> Subcategory:
    return Subcategory.objects.get(slug=slug)


def _get_products_when_searching(query: str) -> list[Product]:
    return Product.in_stock.filter(name__istartswith=query)


def _create_product_in_wishlist(product_id: str, user_id: str) -> FavoriteProduct:
    return FavoriteProduct.objects.create(
        product_id=product_id,
        user_id=user_id,
    )


def _remove_product_from_wishlist(product_id: str, user_id: str) -> FavoriteProduct:
    removed_product = FavoriteProduct.objects.get(
        product_id=product_id,
        user_id=user_id
    )
    removed_product.delete()
    return removed_product


def _get_products_in_wishlist(user: get_user_model()) -> list[Product]:
    favorite_products_ids = [p.product_id for p in user.favoriteproduct_set.all()]
    return Product.in_stock.filter(pk__in=favorite_products_ids)


def _get_current_sort(request: HttpRequest) -> str:
    return request.GET.get("sort", None)
