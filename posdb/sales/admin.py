from django.contrib import admin
from django.utils.html import format_html
from .models import Discount, Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'stock', 'is_active', 'image_preview']
    list_filter   = ['category', 'is_active']
    search_fields = ['name', 'barcode']
    ordering      = ['name']

    def image_preview(self, obj):
        """Show small image preview in admin list"""
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px; width:40px; object-fit:cover; border-radius:6px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Image"


class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 1
    fields = ['product', 'quantity', 'unit_price']


class DiscountInline(admin.StackedInline):
    model  = Discount
    extra  = 0
    fields = ['description', 'amount']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display  = ['description', 'amount', 'order']
    search_fields = ['description', 'order__pk']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'cashier', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['cashier', 'notes']
    ordering      = ['-created_at']
    inlines       = [OrderItemInline, DiscountInline]