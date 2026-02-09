from django.contrib import admin
from .models import Category, Product, ProductImage, Stock


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    max_num = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "final_price",
        "stock_quantity",
        "is_active",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, StockInline]

    @admin.display(description="الكمية المتوفرة")
    def stock_quantity(self, obj):
        """
        عرض كمية المنتج في الأدمن
        آمن في حال ما كان فيه سجل Stock
        """
        if hasattr(obj, "stock"):
            return obj.stock.quantity
        return 0


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main")
    list_filter = ("is_main",)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity")
