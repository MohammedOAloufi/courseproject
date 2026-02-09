from django.shortcuts import render
from .models import Product


def catalog_home(request):
    products = Product.objects.filter(is_active=True).select_related("stock")
    return render(
        request,
        "home.html",
        {
            "products": products
        }
    )
