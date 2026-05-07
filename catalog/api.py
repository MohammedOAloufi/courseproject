from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from orders.models import Order

from .models import Category, Product, Stock


def _serialize_product(product):
    images = list(product.images.all())
    main_image = next((img for img in images if img.is_main), None)
    if main_image is None and images:
        main_image = images[0]

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
@cache_page(60)
def catalog_home_api(request):
    featured_products = (
        Product.objects.filter(is_active=True)
        .select_related("category", "stock")
        .prefetch_related("images")
        .order_by("-created_at")[:6]
    )

    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    # استعلام واحد بدل تحميل كل المنتجات في الذاكرة
    total_stock = (
        Stock.objects.filter(product__is_active=True).aggregate(s=Sum("quantity"))["s"]
        or 0
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