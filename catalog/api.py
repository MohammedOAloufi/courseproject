from django.http import JsonResponse
from django.views.decorators.http import require_GET

from orders.models import Order

from .models import Category, Product


def _serialize_product(product):
    main_image = next(
        (image for image in product.images.all() if image.is_main),
        None,
    )
    if main_image is None:
        main_image = next(iter(product.images.all()), None)

    stock_quantity = getattr(product.stock, "quantity", 0)

    return {
        "id": product.id,
        "name": product.name,
        "category": product.category.name,
        "description": product.description,
        "price": str(product.price),
        "final_price": str(product.final_price),
        "stock_quantity": stock_quantity,
        "image_url": main_image.image.url if main_image else None,
    }


@require_GET
def catalog_home_api(request):
    active_products = Product.objects.filter(is_active=True)
    active_products_with_stock = active_products.select_related("stock")
    featured_products = (
        active_products.select_related("category", "stock")
        .prefetch_related("images")
        .order_by("-created_at")[:6]
    )

    total_products = active_products.count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_stock = sum(
        product.stock.quantity if hasattr(product, "stock") else 0
        for product in active_products_with_stock
    )

    payload = {
        "title": "واجهة المتجر",
        "subtitle": "عالم الالعاب في انتظارك!",
        "summary": (
            f"لديك {total_products} منتج مفعل و{total_categories} تصنيف "
            "يمكن استعراضها من التطبيق الآن."
        ),
        "stats": {
            "products": total_products,
            "categories": total_categories,
            "orders": total_orders,
            "stock": total_stock,
        },
        "featured_products": [
            _serialize_product(product) for product in featured_products
        ],
    }
    return JsonResponse(payload)