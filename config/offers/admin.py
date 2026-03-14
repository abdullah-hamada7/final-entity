from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe   # ← أضف ده لو هتستخدم mark_safe
from .models import Offer, OfferProduct


class OfferProductInline(admin.TabularInline):
    model = OfferProduct
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'offer_type',
        'discount_value_display',
        'start_date',
        'end_date',
        'is_active',
        'is_featured',
        'image_thumbnail',
    )
    
    list_filter = ('offer_type', 'is_active', 'is_featured', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'
    inlines = [OfferProductInline]
    
    fieldsets = (
        ('معلومات العرض الأساسية', {'fields': ('title', 'description', 'image')}),
        ('نوع وقيمة الخصم', {'fields': ('offer_type', 'discount_value')}),
        ('الفترة الزمنية', {'fields': ('start_date', 'end_date')}),
        ('الإعدادات الإضافية', {'fields': ('is_active', 'is_featured', 'badge_text', 'badge_color')}),
    )
    
    @admin.display(description='صورة')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{url}" style="max-height: 60px; border-radius: 4px;" alt="{title}" />',
                url=obj.image.url,
                title=obj.title
            )
        
        # اختيار واحد من الاثنين دول:
        # خيار 1 – format_html مع placeholder
        return format_html('<span style="color: #999;">{}</span>', '—')
        
        # أو خيار 2 – mark_safe (أبسط في الحالة دي)
        # return mark_safe('<span style="color: #999;">—</span>')
    
    @admin.display(description='قيمة الخصم', ordering='discount_value')
    def discount_value_display(self, obj):
        if obj.offer_type == 'percentage':
            return f"{obj.discount_value} %"
        return f"{obj.discount_value} ج.م"