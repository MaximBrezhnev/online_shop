from typing import Any

from django.http import HttpRequest

from commerce.models import Category


def category_context(request: HttpRequest) -> dict[str:Any]:
    categories = Category.objects.all()
    context = {"categories": categories}
    return context
