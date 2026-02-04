from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="اسم التصنيف"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="الاسم المختصر"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="التصنيف الأب"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعل"
    )

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="التصنيف"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="اسم المنتج"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="الاسم المختصر"
    )
    description = models.TextField(
        verbose_name="وصف المنتج"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="سعر الخصم"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعل"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإضافة"
    )

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price or self.price


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="المنتج"
    )
    image = models.ImageField(
        upload_to="products/",
        verbose_name="صورة المنتج"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="صورة رئيسية"
    )

    class Meta:
        verbose_name = "صورة منتج"
        verbose_name_plural = "صور المنتجات"

    def __str__(self):
        return f"صورة - {self.product.name}"


class Stock(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="stock",
        verbose_name="المنتج"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="الكمية المتوفرة"
    )

    class Meta:
        verbose_name = "مخزون"
        verbose_name_plural = "المخزون"

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
