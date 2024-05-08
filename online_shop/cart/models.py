from django.contrib.auth import get_user_model
from django.db import models


class ProductInCart(models.Model):
    product = models.ForeignKey(to="commerce.Product", on_delete=models.CASCADE, verbose_name="Товар")
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
    product = models.ForeignKey(to="commerce.Product", on_delete=models.PROTECT, verbose_name="Товар")
    size = models.CharField(max_length=10, blank=True, null=True, verbose_name="Размер")
    number = models.PositiveIntegerField(verbose_name="Количество")
    order = models.ForeignKey(to="Order", on_delete=models.CASCADE, verbose_name="Заказ")

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Заказанный товар"
        verbose_name_plural = "Заказанные товары"
