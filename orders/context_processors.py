from django.db.models import Sum

from .models import Cart


def cart_count(request):
    """يعرض عدد عناصر السلة في كل القوالب — استعلام واحد فقط."""
    if request.user.is_authenticated:
        result = Cart.objects.filter(user=request.user).aggregate(
            count=Sum("items__quantity")
        )
        return {"cart_count": result["count"] or 0}
    return {"cart_count": 0}
