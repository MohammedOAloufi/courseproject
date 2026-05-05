from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .models import Cart, CartItem, Order, OrderItem, Payment


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _cart_total(cart):
    return sum(
        (item.price_at_time * item.quantity for item in cart.items.all()),
        Decimal("0.00"),
    )


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related("product").prefetch_related("product__images")
    total = _cart_total(cart)
    return render(
        request,
        "orders-templates/cart.html",
        {"cart": cart, "items": items, "total": total},
    )


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    stock_qty = getattr(getattr(product, "stock", None), "quantity", 0)
    if stock_qty <= 0:
        messages.error(request, "هذا المنتج غير متوفر حالياً")
        return redirect("home")

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity, "price_at_time": product.final_price},
    )
    if not created:
        new_qty = item.quantity + quantity
        if new_qty > stock_qty:
            new_qty = stock_qty
            messages.warning(request, f"تم تعديل الكمية للحد المتوفر ({stock_qty})")
        item.quantity = new_qty
        item.price_at_time = product.final_price
        item.save()
    elif quantity > stock_qty:
        item.quantity = stock_qty
        item.save()
        messages.warning(request, f"تم تعديل الكمية للحد المتوفر ({stock_qty})")

    messages.success(request, f"تمت إضافة «{product.name}» إلى السلة")
    return redirect("orders:cart")


@login_required
@require_POST
def update_cart_item(request, item_id):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        item.delete()
        messages.success(request, "تم حذف المنتج من السلة")
        return redirect("orders:cart")

    stock_qty = getattr(getattr(item.product, "stock", None), "quantity", 0)
    if quantity > stock_qty:
        quantity = max(stock_qty, 1)
        messages.warning(request, f"الحد المتاح للمخزون: {stock_qty}")

    item.quantity = quantity
    item.save()
    messages.success(request, "تم تحديث الكمية")
    return redirect("orders:cart")


@login_required
@require_POST
def remove_cart_item(request, item_id):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "تم حذف المنتج من السلة")
    return redirect("orders:cart")


@login_required
def checkout_view(request):
    cart = _get_or_create_cart(request.user)
    items = list(cart.items.select_related("product").all())

    if not items:
        messages.error(request, "السلة فارغة")
        return redirect("orders:cart")

    total = _cart_total(cart)

    if request.method == "POST":
        with transaction.atomic():
            for ci in items:
                stock = getattr(ci.product, "stock", None)
                stock_qty = stock.quantity if stock else 0
                if ci.quantity > stock_qty:
                    messages.error(
                        request,
                        f"الكمية المطلوبة من «{ci.product.name}» غير متوفرة",
                    )
                    return redirect("orders:cart")

            order = Order.objects.create(
                user=request.user,
                status="pending",
                total_price=total,
            )

            for ci in items:
                OrderItem.objects.create(
                    order=order,
                    product_name=ci.product.name,
                    quantity=ci.quantity,
                    price=ci.price_at_time,
                )
                stock = ci.product.stock
                stock.quantity = max(0, stock.quantity - ci.quantity)
                stock.save()

            Payment.objects.create(
                order=order,
                status="success",
                transaction_id=uuid4().hex,
            )
            order.status = "paid"
            order.save()

            cart.items.all().delete()

        messages.success(request, f"تم إنشاء الطلب رقم #{order.id} بنجاح")
        return redirect("orders:order_detail", order_id=order.id)

    return render(
        request,
        "orders-templates/checkout.html",
        {"cart": cart, "items": items, "total": total},
    )


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, "orders-templates/orders_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )
    return render(request, "orders-templates/order_detail.html", {"order": order})
