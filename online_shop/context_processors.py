from django.http import HttpRequest

from commerce.models import Category


def category_context(request: HttpRequest):
    categories = Category.objects.all()
    context = {"categories": categories}
    return context
