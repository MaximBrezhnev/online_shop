from typing import Any

from commerce.models import Category
from django.http import HttpRequest


def category_context(request: HttpRequest) -> dict[str:Any]:
    categories = Category.objects.all()
    context = {"categories": categories}
    return context
