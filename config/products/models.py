from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم الفئة')
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(blank=True, verbose_name='الوصف')
    icon = models.CharField(max_length=50, default='fas fa-medkit', verbose_name='أيقونة')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200, verbose_name='اسم الفئة الفرعية')
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(blank=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'فئة فرعية'
        verbose_name_plural = 'الفئات الفرعية'
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Brand(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم الشركة المصنعة')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    class Meta:
        verbose_name = 'شركة مصنعة'
        verbose_name_plural = 'الشركات المصنعة'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=255, verbose_name='اسم المنتج')
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(verbose_name='الوصف')
    specifications = models.TextField(blank=True, verbose_name='المواصفات')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')
    discount_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='نسبة الخصم %'
    )
    stock = models.IntegerField(default=0, verbose_name='المخزون')
    
    icon = models.CharField(max_length=50, default='fas fa-box', verbose_name='أيقونة')
    is_featured = models.BooleanField(default=False, verbose_name='منتج مميز')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    views = models.IntegerField(default=0, verbose_name='عدد المشاهدات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    @property
    def total_reviews(self):
        return self.reviews.count()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', verbose_name='الصورة')
    is_primary = models.BooleanField(default=False, verbose_name='صورة رئيسية')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    
    class Meta:
        verbose_name = 'صورة منتج'
        verbose_name_plural = 'صور المنتجات'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - صورة {self.order}"

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=255, verbose_name='الميزة')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    
    class Meta:
        verbose_name = 'ميزة منتج'
        verbose_name_plural = 'مميزات المنتجات'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - {self.feature}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم'
    )
    comment = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.product.name} ({self.rating}/5)"