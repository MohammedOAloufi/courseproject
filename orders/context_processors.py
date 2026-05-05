from .models import Cart


def cart_count(request):
    """يعرض عدد عناصر السلة في كل القوالب."""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = sum(item.quantity for item in cart.items.all())
            return {"cart_count": count}
    return {"cart_count": 0}
