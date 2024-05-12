from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.forms import CheckoutForm
from cart.models import ProductInCart, Order, OrderItem
from cart.services import _get_available_sizes
from commerce.models import SizeAndNumber, Product


class AddToCartTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_add_to_cart_product_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
            "is_size": 0,
        }
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"]
        ).number
        path = reverse("add_to_cart")
        response = self.client.get(path, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "product",
                kwargs={
                    "product_slug": Product.objects.get(pk=data["product_id"]).slug
                }
            )
        )

        self.assertTrue(
            number_before == SizeAndNumber.objects.get(
                product_id=data["product_id"]
            ).number + 1
        )
        self.assertTrue(
            ProductInCart.objects.filter(
                user_id=data["user_id"],
                product_id=data["product_id"],
                size=None,
                number=1,
            ).exists()
        )

    def test_add_to_cart_product_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "is_size": 1,
        }
        path = reverse("add_to_cart")
        response = self.client.get(path, data)
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(context["product_id"], str(data["product_id"]))
        self.assertEqual(context["user_id"], str(data["user_id"]))
        self.assertEqual(context["sizes"], _get_available_sizes(
            str(data["product_id"]), str(data["user_id"])
        ))


class ChooseSizeTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_choose_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": 48,
        }
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number
        path = reverse("choose_size")
        response = self.client.get(path, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "product",
                kwargs={
                    "product_slug": Product.objects.get(pk=data["product_id"]).slug
                }
            )
        )
        self.assertTrue(
            number_before == SizeAndNumber.objects.get(
                product_id=data["product_id"],
                size=data["size"]
            ).number + 1
        )
        self.assertTrue(
            ProductInCart.objects.filter(
                user_id=data["user_id"],
                product_id=data["product_id"],
                size=data["size"],
                number=1,
            ).exists()
        )


class RemoveFromCartTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def setUp(self):
        ProductInCart.objects.bulk_create([
            ProductInCart(
                user_id=2,
                product_id=4,
                size=48,
                number=1,
            ),
            ProductInCart(
                user_id=2,
                product_id=59,
                number=1
            )
        ])
        user = get_user_model().objects.get(
            email="user1@mail.ru",
        )
        self.client.force_login(user)

    def test_remove_from_cart_product_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
        }
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"]
        ).number
        number_in_cart = ProductInCart.objects.get(
                product_id=data["product_id"],
                user_id=data["user_id"]
            ).number
        path = reverse("remove_from_cart")
        response = self.client.get(path, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("list_of_products_in_cart"))

        self.assertFalse(
            ProductInCart.objects.filter(
                product_id=data["product_id"],
                user_id=data["user_id"]
            ).exists()
        )
        self.assertTrue(
            number_before == SizeAndNumber.objects.get(
                product_id=data["product_id"],
            ).number - number_in_cart
        )

    def test_remove_from_cart_product_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": 48,
        }
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number
        number_in_cart = ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number
        path = reverse("remove_from_cart")
        response = self.client.get(path, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("list_of_products_in_cart"))

        self.assertFalse(
            ProductInCart.objects.filter(
                product_id=data["product_id"],
                user_id=data["user_id"],
                size=data["size"]
            ).exists()
        )
        self.assertTrue(
            number_before == SizeAndNumber.objects.get(
                product_id=data["product_id"],
                size=data["size"]
            ).number - number_in_cart
        )


class CartTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
    ]

    def setUp(self):
        ProductInCart.objects.bulk_create([
            ProductInCart(
                user_id=2,
                product_id=4,
                size=48,
                number=1,
            ),
            ProductInCart(
                user_id=2,
                product_id=59,
                number=1
            )
        ])

    def test_cart(self):
        user = get_user_model().objects.get(
            email="user1@mail.ru",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("list_of_products_in_cart"))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "cart/cart.html")
        self.assertEqual(context["title"], "Корзина")

        self.assertEqual(list(context["products_in_cart"]), list(ProductInCart.objects.filter(user=user)))

    def test_cart_login_required(self):
        response = self.client.get(reverse("list_of_products_in_cart"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("message_about_cart")+'?next=/cart/list-of-products-in-cart/'
        )

    def test_message_about_cart(self):
        response = self.client.get(reverse("list_of_products_in_cart"), follow=True)
        context = response.context
        self.assertTemplateUsed(response, "message_about_permission.html")
        self.assertTrue(context["title"], "Корзина недоступна")
        self.assertTrue(context["section"], "корзина")


class IncreaseTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def setUp(self):
        ProductInCart.objects.bulk_create([
            ProductInCart(
                user_id=2,
                product_id=4,
                size=48,
                number=1,
            ),
            ProductInCart(
                user_id=2,
                product_id=59,
                number=1
            )
        ])
        user = get_user_model().objects.get(
            pk=2
        )
        self.client.force_login(user)

    def test_increase_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
        }

        number_in_cart = ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number
        size_and_number = SizeAndNumber.objects.get(
            product_id=data["product_id"]
        )
        size_and_number.number = 1
        size_and_number.save()

        response = self.client.get(reverse("increase"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )

        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"]
        ).number, 0)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number, number_in_cart + 1)

    def test_not_increase_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
        }

        number_in_cart = ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number
        size_and_number = SizeAndNumber.objects.get(
            product_id=data["product_id"]
        )
        size_and_number.number = 0
        size_and_number.save()

        response = self.client.get(reverse("increase"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )

        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"]
        ).number, 0)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number, number_in_cart)

    def test_increase_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": "48",
        }
        number_in_cart = ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number
        size_and_number = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        )
        size_and_number.number = 1
        size_and_number.save()

        response = self.client.get(reverse("increase"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )

        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number, 0)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number, number_in_cart + 1)

    def test_not_increase_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": "48",
        }
        number_in_cart = ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number
        size_and_number = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        )
        size_and_number.number = 0
        size_and_number.save()

        response = self.client.get(reverse("increase"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )

        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number, 0)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number, number_in_cart)


class ReduceTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def setUp(self):
        user = get_user_model().objects.get(
            pk=2
        )
        self.client.force_login(user)

    def test_reduce_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
        }
        number_in_cart = 2
        ProductInCart.objects.create(
            user_id=data["user_id"],
            product_id=data["product_id"],
            number=number_in_cart
        )
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
        ).number

        response = self.client.get(reverse("reduce"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )
        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
        ).number, number_before + 1)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number, number_in_cart - 1)

    def test_not_reduce_without_size(self):
        data = {
            "user_id": 2,
            "product_id": 59,
        }
        number_in_cart = 1
        ProductInCart.objects.create(
            user_id=data["user_id"],
            product_id=data["product_id"],
            number=number_in_cart
        )
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
        ).number

        response = self.client.get(reverse("reduce"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )
        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
        ).number, number_before)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
        ).number, number_in_cart)

    def test_reduce_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": "48",
        }
        number_in_cart = 2
        ProductInCart.objects.create(
            user_id=data["user_id"],
            product_id=data["product_id"],
            size=data["size"],
            number=number_in_cart
        )
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number

        response = self.client.get(reverse("reduce"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )
        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number, number_before + 1)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number, number_in_cart - 1)

    def test_not_reduce_with_size(self):
        data = {
            "user_id": 2,
            "product_id": 4,
            "size": "48",
        }
        number_in_cart = 1
        ProductInCart.objects.create(
            user_id=data["user_id"],
            product_id=data["product_id"],
            size=data["size"],
            number=number_in_cart
        )
        number_before = SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number

        response = self.client.get(reverse("reduce"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("list_of_products_in_cart")
        )
        self.assertEqual(SizeAndNumber.objects.get(
            product_id=data["product_id"],
            size=data["size"]
        ).number, number_before)
        self.assertEqual(ProductInCart.objects.get(
            product_id=data["product_id"],
            user_id=data["user_id"],
            size=data["size"]
        ).number, number_in_cart)


class CheckoutTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/users_user.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def setUp(self):
        user = get_user_model().objects.get(pk=2)
        self.user = user
        self.client.force_login(user)

        ProductInCart.objects.bulk_create(
            [
                ProductInCart(
                    user_id=2,
                    product_id=4,
                    size=48,
                    number=1,
                ),
                ProductInCart(
                    user_id=2,
                    product_id=59,
                    number=1
                )
            ]
        )

    def test_get_checkout_form(self):
        response = self.client.get(reverse("checkout"))
        context = response.context
        total_price = sum(p.product.price * p.number for p in ProductInCart.objects.filter(user=self.user))
        total_quantity = sum(p.number for p in ProductInCart.objects.filter(user=self.user))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "cart/checkout.html")
        self.assertEqual(context["title"], "Оформление заказа")
        self.assertEqual(context["total_price"], total_price)
        self.assertEqual(context["total_quantity"], total_quantity)

    def test_form_with_incorrect_credentials(self):
        data = [
            (
                {
                    "surname": "Иванов3",
                    "name": "Иван",
                    "middle_name": "Иванович",
                    "address": "ул. Иванова, 5",
                    "phone_number": "+79997778822"
                },
                ['Фамилия должна содержать только буквы и дефисы.']
            ),
            (
                {
                    "surname": "Иванов",
                    "name": "Иван3",
                    "middle_name": "Иванович",
                    "address": "ул. Иванова, 5",
                    "phone_number": "+79997778822",
                },
                ['Имя должно содержать только буквы и дефисы.']
            ),
            (
                {
                    "surname": "Иванов",
                    "name": "Иван",
                    "middle_name": "Иванович3",
                    "address": "ул. Иванова, 5",
                    "phone_number": "+79997778822",
                },
                ['Отчество должно содержать только буквы и дефисы.']
            ),
            (
                {
                    "surname": "Иванов",
                    "name": "Иван",
                    "middle_name": "Иванович",
                    "address": "ул. Иванова, 5",
                    "phone_number": "000",
                },
                ['Некорректный номер телефона.']
            )
        ]

        fields = ["surname", "name", "middle_name", "phone_number"]
        number_of_incorrect_field = 0
        for case in data:
            credentials = case[0]
            expected = case[1]
            with self.subTest(credentials=credentials):
                form = CheckoutForm(credentials)
                self.assertFalse(form.is_valid())
                self.assertEqual(
                    form.errors[fields[number_of_incorrect_field]],
                    expected
                )
                number_of_incorrect_field += 1

    def test_post_correct_credentials(self):
        data = {
            "surname": "Иванов",
            "name": "Иван",
            "middle_name": "Иванович",
            "address": "ул. Иванова, 5",
            "phone_number": "+79997778822",
        }

        response = self.client.post(reverse("checkout"), data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("message_about_order"))

        order = Order.objects.filter(
            surname=data["surname"],
            name=data["name"],
            middle_name=data["middle_name"],
            address=data["address"],
            phone_number=data["phone_number"],
            status=0,
        )
        self.assertTrue(order.exists())
        self.assertTrue(OrderItem.objects.filter(
            product_id=4,
            number=1,
            size=48,
            order=order[0]
        ).exists())
        self.assertTrue(OrderItem.objects.filter(
            product_id=59,
            number=1,
            order=order[0]
        ))

    def test_message_about_order(self):
        data = {
            "surname": "Иванов",
            "name": "Иван",
            "middle_name": "Иванович",
            "address": "ул. Иванова, 5",
            "phone_number": "+79997778822",
        }
        response = self.client.post(
            reverse("checkout"),
            data,
            follow=True
        )
        context = response.context

        self.assertTemplateUsed(response, "cart/message_about_order.html")
        self.assertEqual(context["title"], "Заказ оформлен")














