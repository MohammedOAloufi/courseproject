from django.db import models
from accounts.models import User
from catalog.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="المستخدم"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "سلة"
        verbose_name_plural = "السلال"

    def __str__(self):
        return f"سلة - {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="السلة"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="المنتج"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="الكمية"
    )
    price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر وقت الإضافة"
    )

    class Meta:
        verbose_name = "عنصر سلة"
        verbose_name_plural = "عناصر السلة"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "قيد الانتظار"),
        ("paid", "مدفوع"),
        ("cancelled", "ملغي"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="المستخدم"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="حالة الطلب"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="الإجمالي"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f"طلب رقم #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الطلب"
    )
    product_name = models.CharField(
        max_length=200,
        verbose_name="اسم المنتج"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="الكمية"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر"
    )

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلب"

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("success", "ناجح"),
        ("failed", "فشل"),
        ("pending", "قيد المعالجة"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="الطلب"
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        verbose_name="حالة الدفع"
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="رقم العملية"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الدفع"
    )

    class Meta:
        verbose_name = "عملية دفع"
        verbose_name_plural = "عمليات الدفع"

    def __str__(self):
        return f"دفع الطلب #{self.order.id}"
