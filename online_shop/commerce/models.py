from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class DisplayMixin:
    def __str__(self):
        return self.__getattribute__("name")


class ProductsInStockManager(models.Manager):
    def get_queryset(self):
        products = list(Product.objects.all())
        products_in_stock = []
        for product in products:
            total = sum(item.number for item in product.size_and_number_set.all())
            if total > 0:
                products_in_stock.append(product)

        return super().get_queryset().filter(pk__in=[p.pk for p in products_in_stock])


class Product(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    photo = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        blank=True,
        null=True,
        verbose_name="Фотография"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Время появления")
    category = models.ForeignKey(to="Category", on_delete=models.PROTECT, verbose_name="Категория")
    subcategory = models.ForeignKey(to="Subcategory", on_delete=models.PROTECT, verbose_name="Подкатегория")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    objects = models.Manager()
    in_stock = ProductsInStockManager()


class Category(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse("products_by_category", kwargs={"category_slug": self.slug})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Subcategory(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse(
            "products_by_subcategory",
            kwargs={"category_slug": self.slug, }
        )

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class SizeAndNumber(models.Model):
    size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Размер")
    number = models.PositiveIntegerField(verbose_name='Количество')
    product = models.ForeignKey(
        to="Product",
        on_delete=models.CASCADE,
        related_name="size_and_number_set",
        verbose_name="Товар"
    )

    def __str__(self):
        if self.size:
            return f"Размер {self.__getattribute__('size')} товара {self.product.name}"
        return f"Количество товаров {self.product.name}"

    class Meta:
        ordering = ["size"]
        verbose_name = "Размер и количество"
        verbose_name_plural = "Размеры и количество"


class FavoriteProduct(models.Model):
    product = models.ForeignKey(to="Product", on_delete=models.CASCADE, verbose_name="Товар")
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ("user", "product", )
        verbose_name = "Товар в избранном"
        verbose_name_plural = "Избранное"


class ProductInCart(models.Model):
    product = models.ForeignKey(to="Product", on_delete=models.CASCADE, verbose_name="Товар")
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name="Пользователь")
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Размер")
    number = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Корзина"


class Order(models.Model):
    class Status(models.IntegerChoices):
        ON_WAY = 0, 'В Пути'
        DELIVERED = 1, 'Доставлен'

    surname = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество")
    address = models.CharField(max_length=100, verbose_name="Адрес")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    status = models.BooleanField(
        choices=map(lambda x: (bool(x[0]), x[1]),  Status.choices),
        default=Status.ON_WAY,
        verbose_name="Статус"
    )
    created_at = models.TimeField(auto_now_add=True, verbose_name="Время оформления")

    def __str__(self):
        return f"Заказ №{self.id}"

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    product = models.ForeignKey(to="Product", on_delete=models.PROTECT, verbose_name="Товар")
    size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Размер")
    number = models.PositiveIntegerField(verbose_name="Количество")
    order = models.ForeignKey(to="Order", on_delete=models.CASCADE, verbose_name="Заказ")

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Заказанный товар"
        verbose_name_plural = "Заказанные товары"


