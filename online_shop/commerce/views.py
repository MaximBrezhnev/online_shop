from django.views.generic import TemplateView, DetailView

from commerce.models import Product, Category


class IndexListView(TemplateView):
    template_name = "commerce/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all().order_by("-created_at")
        context["categories"] = Category.objects.all()
        return context


class ProductView(DetailView):
    slug_url_kwarg = "product_slug"
    template_name = "commerce/product.html"
    model = Product
    context_object_name = "product"
