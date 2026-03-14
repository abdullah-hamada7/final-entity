from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'total_items', 'total_price', 'created_at', 'view_cart', 'status')
    list_filter = ('created_at', 'status')
    search_fields = ('user__full_name', 'session_key')
    readonly_fields = ('total_price', 'total_items')
    inlines = [CartItemInline]

    def view_cart(self, obj):
      
        return format_html('<a class="button" href="/admin/orders/cart/{}/change/">عرض</a>', obj.id)
    view_cart.short_description = 'تفاصيل السلة'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'phone', 'status', 'total_amount', 'confirm_button', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__full_name', 'phone', 'email')
    readonly_fields = ('order_number', 'whatsapp_link', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('معلومات العميل', {
            'fields': ('full_name', 'phone', 'email', 'address', 'notes')
        }),
        ('التفاصيل المالية', {
            'fields': ('total_amount',)
        }),
        ('واتساب', {
            'fields': ('whatsapp_link',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['generate_whatsapp_links', 'confirm_selected_orders']

    def generate_whatsapp_links(self, request, queryset):
        for order in queryset:
            order.generate_whatsapp_link()
        self.message_user(request, f'تم إنشاء روابط واتساب لـ {queryset.count()} طلب')
    generate_whatsapp_links.short_description = 'إنشاء روابط واتساب'

    def confirm_selected_orders(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'تم تأكيد {updated} طلب بنجاح ✅')
    confirm_selected_orders.short_description = 'تأكيد الطلبات المحددة'

    def confirm_button(self, obj):
        return format_html(
            '<a class="button" style="background:green;color:white;padding:5px 10px;border-radius:5px;" '
            'href="/admin/app_name/order/{}/confirm/">تأكيد الطلب</a>', obj.id
        )
    confirm_button.short_description = 'تأكيد'