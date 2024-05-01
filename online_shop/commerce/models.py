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
        for product in products:
            total = sum(item.number for item in product.size_and_number_set.all())
            if total <= 0:
                products.remove(product)

        return super().get_queryset().filter(pk__in=[p.pk for p in products])


class Product(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    photo = models.ImageField(
        upload_to="products/%Y/%m/%d/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    category = models.ForeignKey(to="Category", on_delete=models.PROTECT)
    subcategory = models.ForeignKey(to="Subcategory", on_delete=models.PROTECT)

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    objects = models.Manager()
    in_stock = ProductsInStockManager()


class Category(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse("products_by_category", kwargs={"category_slug": self.slug})


class Subcategory(DisplayMixin, models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse(
            "products_by_subcategory",
            kwargs={"category_slug": self.slug, }
        )


class SizeAndNumber(models.Model):
    size = models.CharField(max_length=10, blank=True, null=True)
    number = models.PositiveIntegerField()
    product = models.ForeignKey(
        to="Product",
        on_delete=models.CASCADE,
        related_name="size_and_number_set"
    )

    def __str__(self):
        return self.__getattribute__("value")


class FavoriteProduct(models.Model):
    product = models.ForeignKey(to="Product", on_delete=models.CASCADE)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ("user", "product", )


class ProductInCart(models.Model):
    product = models.ForeignKey(to="Product", on_delete=models.CASCADE)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    size = models.CharField(max_length=50, blank=True, null=True)
    number = models.PositiveIntegerField()

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ("user", "product", "size", )




