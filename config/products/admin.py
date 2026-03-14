from django.contrib import admin
from .models import Category, SubCategory, Brand, Product, ProductImage, ProductFeature, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'order')

class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 3
    fields = ('feature', 'order')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_percentage', 'final_price', 'stock', 'is_featured', 'is_active', 'views')
    list_filter = ('category', 'brand', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [ProductImageInline, ProductFeatureInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'category', 'subcategory', 'brand')
        }),
        ('التفاصيل', {
            'fields': ('description', 'specifications', 'icon')
        }),
        ('الأسعار والمخزون', {
            'fields': ('price', 'discount_percentage', 'stock')
        }),
        ('الإعدادات', {
            'fields': ('is_featured', 'is_active')
        }),
        ('الإحصائيات', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__full_name', 'comment')
    readonly_fields = ('created_at',)