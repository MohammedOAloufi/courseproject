from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product, Stock

from .models import Cart, CartItem, Order, OrderItem, Payment


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _cart_total(items):
    """احسب إجمالي السلة من قائمة العناصر المحمّلة مسبقاً."""
    return sum(
        (item.price_at_time * item.quantity for item in items),
        Decimal("0.00"),
    )


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related("product").prefetch_related("product__images")
    total = _cart_total(items)
    return render(
        request,
        "orders-templates/cart.html",
        {"cart": cart, "items": items, "total": total},
    )


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("stock"), id=product_id, is_active=True
    )

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
    item = get_object_or_404(
        CartItem.objects.select_related("product__stock"), id=item_id, cart=cart
    )

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
    # جلب العناصر مع المنتج والمخزون دفعة واحدة
    items = list(cart.items.select_related("product__stock").all())

    if not items:
        messages.error(request, "السلة فارغة")
        return redirect("orders:cart")

    total = _cart_total(items)

    if request.method == "POST":
        with transaction.atomic():
            product_ids = [ci.product_id for ci in items]
            # قفل صفوف المخزون لضمان التناسق عند الطلبات المتزامنة
            locked_stocks = {
                s.product_id: s
                for s in Stock.objects.select_for_update().filter(
                    product_id__in=product_ids
                )
            }

            for ci in items:
                stock = locked_stocks.get(ci.product_id)
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

            # إدراج عناصر الطلب دفعة واحدة بدل insert لكل عنصر
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product_name=ci.product.name,
                    quantity=ci.quantity,
                    price=ci.price_at_time,
                )
                for ci in items
            ])

            # تحديث المخزون باستخدام F() لتجنب race conditions
            for ci in items:
                Stock.objects.filter(product_id=ci.product_id).update(
                    quantity=F("quantity") - ci.quantity
                )

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
