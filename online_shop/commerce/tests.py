from http import HTTPStatus
from math import ceil

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import ProductInCart
from commerce.models import Product, FavoriteProduct, Category, Subcategory
from commerce.views import ProductsByCategoryView, IndexListView, ProductsBySubcategoryView, ProductsBySearchView, \
    FavoriteProductsView


class IndexListTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/list_of_products.html")
        self.assertEqual(context["title"], "Главная")
        self.assertEqual(context["header"], "Новинки")

    def test_index_list_first_page(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(
            list(response.context["products"]),
            list(Product.in_stock.all())[:IndexListView.paginate_by]
        )

    def test_index_list_last_page(self):
        response = self.client.get(reverse("home") + "?page=4")

        self.assertEqual(
            list(response.context["products"]),
            list(Product.in_stock.all())[18:21]
        )


class ProductTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json",
        "fixtures/users_user.json"
    ]

    def setUp(self):
        user = get_user_model().objects.get(pk=2)
        self.client.force_login(user)

    def test_product_general(self):
        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/product.html")
        self.assertEqual(
            response.context["title"],
            Product.in_stock.get(slug="pidzhak").name
        )

    def test_product_is_favorite(self):
        FavoriteProduct.objects.create(
            user_id=2,
            product=Product.objects.get(slug="pidzhak")
        )
        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))

        self.assertTrue(response.context["is_favorite"])

    def test_product_is_not_favorite(self):
        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))

        self.assertFalse(response.context["is_favorite"])

    def test_product_with_size_is_not_in_cart(self):
        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))
        context = response.context

        self.assertTrue(context["is_size"])
        self.assertFalse(context["in_cart"])
        self.assertTrue(context["not_all_sizes_in_cart"])

    def test_not_all_sizes_in_cart(self):
        ProductInCart.objects.create(
            user_id=2,
            product=Product.objects.get(slug="pidzhak"),
            size=48,
            number=1,
        )

        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))
        context = response.context

        self.assertTrue(context["is_size"])
        self.assertFalse(context["in_cart"])
        self.assertTrue(context["not_all_sizes_in_cart"])

    def test_all_sizes_in_cart(self):
        ProductInCart.objects.create(
            user_id=2,
            product=Product.objects.get(slug="pidzhak"),
            size=48,
            number=1,
        )
        ProductInCart.objects.create(
            user_id=2,
            product=Product.objects.get(slug="pidzhak"),
            size=50,
            number=1,
        )

        response = self.client.get(reverse("product", kwargs={"product_slug": "pidzhak"}))
        context = response.context

        self.assertTrue(context["is_size"])
        self.assertFalse(context["in_cart"])
        self.assertFalse(context["not_all_sizes_in_cart"])

    def test_product_without_size_is_not_in_cart(self):
        response = self.client.get(reverse("product", kwargs={"product_slug": "remen-guess"}))
        context = response.context

        self.assertFalse(context["is_size"])
        self.assertFalse(context["in_cart"])
        self.assertTrue(context["not_all_sizes_in_cart"])

    def test_product_without_size_is_in_cart(self):
        ProductInCart.objects.create(
            user_id=2,
            product=Product.objects.get(slug="remen-guess"),
            number=1
        )

        response = self.client.get(reverse("product", kwargs={"product_slug": "remen-guess"}))
        context = response.context

        self.assertFalse(context["is_size"])
        self.assertTrue(context["in_cart"])
        self.assertTrue(context["not_all_sizes_in_cart"])


class ProductsByCategoryTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_products_by_category(self):
        slug = "muzhchinam"
        response = self.client.get(reverse(
            "products_by_category", kwargs={"category_slug": slug}
        ))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/categories.html")

        self.assertEqual(context["title"], Category.objects.get(slug=slug).name)
        self.assertEqual(context["cat_selected"], Category.objects.get(slug=slug))
        self.assertEqual(list(context["subcategories"]), list(Subcategory.objects.all()))

    def test_products_by_category_first_page(self):
        slug = "muzhchinam"
        response = self.client.get(reverse(
            "products_by_category", kwargs={"category_slug": slug}
        ))
        context = response.context

        self.assertEqual(list(context["products"]), list(Product.in_stock.filter(category__slug=slug))[:6])

    def test_products_by_category_last_page(self):
        slug = "muzhchinam"
        number_of_pages = ceil(len(Product.objects.filter(category__slug=slug)) / ProductsByCategoryView.paginate_by)
        response = self.client.get(reverse(
            "products_by_category", kwargs={"category_slug": slug}
        ) + f"?page={number_of_pages}")
        context = response.context

        number_of_products_on_last_page = (len(Product.objects.filter(category__slug=slug)) -
                                           ProductsByCategoryView.paginate_by) * (number_of_pages - 1)
        self.assertEqual(list(context["products"]), list(Product.in_stock.filter(category__slug=slug))[
                                                    -number_of_products_on_last_page:
                                                    ])

    def test_products_by_category_first_page_price_desc(self):
        slug = "muzhchinam"
        response = self.client.get(reverse(
            "products_by_category", kwargs={"category_slug": slug}
        ) + "?sort=price_desc")
        context = response.context

        self.assertEqual(
            list(context["products"]),
            list(Product.in_stock.filter(category__slug=slug).order_by("-price"))[:ProductsByCategoryView.paginate_by]
        )

    def test_products_by_category_last_page_price_desc(self):
        slug = "muzhchinam"
        number_of_pages = ceil(len(Product.objects.filter(category__slug=slug)) / ProductsByCategoryView.paginate_by)
        response = self.client.get(reverse(
            "products_by_category", kwargs={"category_slug": slug}
        ) + f"?page={number_of_pages}&sort=price_desc")
        context = response.context

        number_of_products_on_last_page = (len(Product.objects.filter(category__slug=slug)) -
                                           ProductsByCategoryView.paginate_by) * (number_of_pages - 1)
        self.assertEqual(list(context["products"]), list(Product.in_stock.filter(category__slug=slug)
                                                         .order_by("-price"))[
                                                    -number_of_products_on_last_page:
                                                    ])


class ProductsBySubcategoryTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_products_by_subcategory(self):
        cat_slug = "muzhchinam"
        subcat_slug = "obuv"
        title = "Мужчинам: обувь"

        response = self.client.get(reverse(
            "products_by_subcategory", kwargs={"category_slug": cat_slug, "subcategory_slug": subcat_slug}
        ))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed("commerce/subcategories.html")

        self.assertEqual(context["title"], title)
        self.assertEqual(context["cat_selected"], Category.objects.get(slug=cat_slug))
        self.assertEqual(context["subcategory_selected"], Subcategory.objects.get(slug=subcat_slug))
        self.assertEqual(list(context["subcategories"]), list(Subcategory.objects.all()))

    def test_products_by_subcategory_first_page(self):
        cat_slug = "muzhchinam"
        subcat_slug = "obuv"
        response = self.client.get(reverse(
            "products_by_subcategory", kwargs={"category_slug": cat_slug, "subcategory_slug": subcat_slug}
        ))
        context = response.context

        self.assertEqual(list(context["products"]), list(Product.in_stock.filter(
            category__slug=cat_slug, subcategory__slug=subcat_slug,
        ))[:ProductsBySubcategoryView.paginate_by])

    def test_products_by_subcategory_first_page_price_asc(self):
        cat_slug = "muzhchinam"
        subcat_slug = "obuv"
        response = self.client.get(reverse(
            "products_by_subcategory", kwargs={"category_slug": cat_slug, "subcategory_slug": subcat_slug}
        ) + "?sort=price_asc")
        context = response.context

        self.assertEqual(list(context["products"]), list(Product.in_stock.filter(
            category__slug=cat_slug, subcategory__slug=subcat_slug,
        ).order_by("price"))[:ProductsBySubcategoryView.paginate_by])


class SearchTestCase(TestCase):
    def test_get_search_page(self):
        response = self.client.get(reverse("search"))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/search.html")
        self.assertEqual(context["title"], "Поиск")
        self.assertEqual(context["previous_page"], None)


class ProductsBySearchTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json"
    ]

    def test_products_by_search(self):
        query = "кр"
        response = self.client.get(reverse("products_by_search") + f"?query={query}")
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/products_by_search.html")
        self.assertEqual(context["title"], "Товары по запросу")
        self.assertEqual(context["current_query"], query)

    def test_products_by_search_first_page(self):
        query = "кр"
        response = self.client.get(reverse("products_by_search") + f"?query={query}")

        self.assertEqual(
            list(response.context["products"]),
            list(Product.in_stock.filter(name__istartswith=query))[:ProductsBySearchView.paginate_by]
        )

    def test_products_by_search_first_page_date(self):
        query = "кр"
        response = self.client.get(reverse("products_by_search") + f"?query={query}&sort=date")

        self.assertEqual(
            list(response.context["products"]),
            list(Product.in_stock.filter(name__istartswith=query))[:ProductsBySearchView.paginate_by]
        )


class AddToWishlistTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json",
        "fixtures/users_user.json"
    ]

    def test_add_to_wishlist(self):
        user_id = 2
        product_id = 59

        user = get_user_model().objects.get(pk=user_id)
        self.client.force_login(user)

        response = self.client.get(
            reverse(
                "add_to_wishlist",
                kwargs={"product_id": product_id, "user_id": user_id}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "product",
                kwargs={"product_slug": Product.objects.get(pk=product_id).slug}
            )
        )

        self.assertTrue(FavoriteProduct.objects.filter(
            product_id=product_id, user_id=user_id
        ).exists())

    def test_add_to_wishlist_without_auth(self):
        response = self.client.get(reverse("message_about_wishlist"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "message_about_permission.html")

        self.assertEqual(response.context["title"], "Избранное недоступно")
        self.assertEqual(response.context["section"], "избранное")


class RemoveFromWishlistTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json",
        "fixtures/users_user.json"
    ]

    def test_remove_from_wishlist(self):
        user_id = 2
        product_id = 59

        FavoriteProduct.objects.create(
            product_id=product_id,
            user_id=user_id
        )

        response = self.client.get(reverse("remove_from_wishlist", kwargs={
            "product_id": product_id, "user_id": user_id
        }
                                           ))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                "product",
                kwargs={"product_slug": Product.objects.get(pk=product_id).slug}
            )
        )

        self.assertFalse(FavoriteProduct.objects.filter(
            product_id=product_id, user_id=user_id
        ).exists())


class FavoriteProductsTestCase(TestCase):
    fixtures = [
        "fixtures/commerce_category.json",
        "fixtures/commerce_subcategory.json",
        "fixtures/commerce_product.json",
        "fixtures/commerce_sizeandnumber.json",
        "fixtures/users_user.json"
    ]

    def test_favorite_products(self):
        user_id = 2
        product_id_1 = 59
        product_id_2 = 1

        FavoriteProduct.objects.create(user_id=user_id, product_id=product_id_1)
        FavoriteProduct.objects.create(user_id=user_id, product_id=product_id_2)

        user = get_user_model().objects.get(pk=user_id)
        self.client.force_login(user)

        response = self.client.get(reverse("list_of_favorite"))
        context = response.context

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "commerce/list_of_products.html")

        self.assertEqual(context["title"], "Избранное")
        self.assertEqual(context["header"], "Избранное")
        self.assertEqual(
            context["message"],
            ("Учтите, что "
             "товары, которых в данный момент нет в наличии, "
             "не отображаются в избранном")
        )

        self.assertEqual(
            list(context["products"]),
            list(Product.objects.filter(pk__in=[product_id_1, product_id_2]))
            [:FavoriteProductsView.paginate_by]
        )

    def test_message_about_permission(self):
        response = self.client.get(reverse("list_of_favorite"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse("message_about_wishlist") +
            "?next=/commerce/wishlist/list-of-favorite/"
        )

