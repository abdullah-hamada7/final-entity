from django.db import models
from django.utils import timezone
from products.models import Product

class Offer(models.Model):
    OFFER_TYPES = [
        ('percentage', 'نسبة مئوية'),
        ('fixed', 'مبلغ ثابت'),
    ]
    
    title = models.CharField(max_length=255, verbose_name='عنوان العرض')
    description = models.TextField(verbose_name='الوصف')
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قيمة الخصم')
    image = models.ImageField(
        upload_to='offers/images/',
        verbose_name='صورة العرض',
        null=True,           # اختياري → يسمح بعرض بدون صورة
        blank=True,          # اختياري → مش مطلوب في الفورم
        # default='offers/default-offer.jpg'   ← اختياري لو عندك صورة افتراضية
    )
    start_date = models.DateTimeField(verbose_name='تاريخ البدء')
    end_date = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    is_featured = models.BooleanField(default=False, verbose_name='عرض مميز')
    
    badge_text = models.CharField(max_length=50, default='خصم', verbose_name='نص الشارة')
    badge_color = models.CharField(max_length=20, default='#FFD700', verbose_name='لون الشارة')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عرض'
        verbose_name_plural = 'العروض'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class OfferProduct(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    
    class Meta:
        verbose_name = 'منتج في العرض'
        verbose_name_plural = 'منتجات العروض'
        unique_together = ('offer', 'product')
    
    def __str__(self):
         return str(self.product)
