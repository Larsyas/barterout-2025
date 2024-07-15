from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity',
                       'product_price', 'ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'email',
                    'order_total', 'created_at')
    list_display_links = ('order_number', 'order_total',)

    readonly_fields = ('created_at',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
