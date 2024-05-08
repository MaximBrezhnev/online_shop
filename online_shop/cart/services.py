from typing import Optional

from django.contrib.auth import get_user_model

from cart.models import ProductInCart, Order, OrderItem
from commerce.models import Product, SizeAndNumber


def _get_product_by_product_id(product_id: str) -> Product:
    return Product.in_stock.get(pk=product_id)


def _get_available_sizes(user_id: str, product_id: str) -> list[int]:
    product = _get_product_by_product_id(product_id)

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
    return sizes


def _change_size_and_number(product_id: str) -> None:
    product = _get_product_by_product_id(product_id)

    size_and_number = product.size_and_number_set.all()[0]
    size_and_number.number -= 1
    size_and_number.save()


def _create_product_in_cart(
        product_id: str,
        user_id: str,
        number: int,
        size: Optional[str] = None
) -> ProductInCart:
    if size is None:
        return ProductInCart.objects.create(
            product_id=product_id,
            user_id=user_id,
            number=number,
        )
    return ProductInCart.objects.create(
            product_id=product_id,
            user_id=user_id,
            size=size,
            number=number,
        )


def _get_product_in_cart(
        product_id: str,
        user_id: str,
        size: Optional[str] = None
) -> ProductInCart:
    if size is None:
        return ProductInCart.objects.get(
            product_id=product_id,
            user_id=user_id
        )
    return ProductInCart.objects.get(
        product_id=product_id,
        user_id=user_id,
        size=size
    )


def _get_size_and_number(product_in_cart: ProductInCart, size: Optional[str] =  None) -> SizeAndNumber:
    if size is None:
        return product_in_cart.product.size_and_number_set.all()[0]
    return product_in_cart.product.size_and_number_set.get(
            size=size
        )


def _restore_size_and_number(product_in_cart: ProductInCart, size: Optional[str] = None) -> None:
    size_and_number = _get_size_and_number(product_in_cart, size)
    size_and_number.number += product_in_cart.number
    size_and_number.save()


def _remove_product(product_id: str, user_id: str, size: Optional[str]) -> None:
    removed_product = _get_product_in_cart(
        product_id=product_id,
        user_id=user_id,
        size=size
    )
    _restore_size_and_number(product_in_cart=removed_product, size=size)
    removed_product.delete()


def _get_products_in_cart_by_user(user: get_user_model()) -> list[ProductInCart]:
    return ProductInCart.objects.filter(
        user=user
    )


def _change_size_and_number_when_increasing(product_id: str, user_id: str, size: Optional[str]) -> None:
    product_in_cart = _get_product_in_cart(
        product_id=product_id,
        user_id=user_id,
        size=size
    )
    size_and_number = _get_size_and_number(
        product_in_cart=product_in_cart,
        size=size
    )
    if size_and_number.number > 0:
        size_and_number.number -= 1
        size_and_number.save()
        product_in_cart.number += 1
        product_in_cart.save()


def _change_size_and_number_when_reducing(product_id: str, user_id: str, size: Optional[str]) -> None:
    product_in_cart = _get_product_in_cart(
        product_id=product_id,
        user_id=user_id,
        size=size
    )
    size_and_number = _get_size_and_number(
        product_in_cart=product_in_cart,
        size=size
    )
    if product_in_cart.number > 1:
        size_and_number.number += 1
        size_and_number.save()
        product_in_cart.number -= 1
        product_in_cart.save()


def _find_total_price(object_list: list[ProductInCart]) -> float:
    return sum(p.product.price * p.number for p in object_list)


def _find_total_quantity(object_list: list[ProductInCart]) -> int:
    return sum(p.number for p in object_list)


def _create_order_items(user: get_user_model(), order: Order) -> None:
    products_in_cart = _get_products_in_cart_by_user(user)

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
