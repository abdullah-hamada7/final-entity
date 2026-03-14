from django.db import models
from django.utils import timezone
from users.models import CustomUser
from products.models import Product


# ========================
# 🛒 موديل السلة
# ========================
class Cart(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشطة'),
        ('ordered', 'تم الطلب'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='حالة السلة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'سلة تسوق'
        verbose_name_plural = 'سلال التسوق'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"سلة {self.user.full_name}"
        return f"سلة جلسة {self.session_key}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='الكمية')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'عنصر في السلة'
        verbose_name_plural = 'عناصر السلة'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        """السعر الكلي = سعر المنتج × الكمية"""
        price = getattr(self.product, 'price', 0) or 0
        quantity = self.quantity or 0
        return price * quantity


# ========================
# 📦 موديل الطلبات
# ========================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, verbose_name='رقم الطلب')
    full_name = models.CharField(max_length=255, verbose_name='الاسم الكامل')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    address = models.TextField(verbose_name='العنوان')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ الإجمالي', default=0)
    whatsapp_link = models.URLField(blank=True, verbose_name='رابط واتساب')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f"طلب #{self.order_number} - {self.user.full_name}"

    def save(self, *args, **kwargs):
        """توليد رقم الطلب تلقائيًا"""
        if not self.order_number:
            import random, string
            self.order_number = 'EM' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    def calculate_total(self):
        """حساب إجمالي الطلب من عناصره"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total

    def confirm_order(self):
        """تأكيد الطلب وتغييره إلى قيد المعالجة"""
        self.calculate_total()
        self.status = 'processing'
        self.save()
        self.generate_whatsapp_link()

    def generate_whatsapp_link(self):
        """توليد رابط واتساب للطلب"""
        company_phone = '+201013928114'
        message = f"طلب جديد من Entity Medical\n"
        message += f"رقم الطلب: {self.order_number}\n"
        message += f"الاسم: {self.full_name}\n"
        message += f"الهاتف: {self.phone}\n"
        message += f"العنوان: {self.address}\n\n"
        message += "تفاصيل الطلب:\n"

        for item in self.items.all():
            message += f"• {item.product_name} x {item.quantity} = {item.subtotal} جنيه\n"

        message += f"\nالمبلغ الإجمالي: {self.total_amount} جنيه"

        from urllib.parse import quote
        encoded_message = quote(message)
        self.whatsapp_link = f"https://wa.me/{company_phone.replace('+', '')}?text={encoded_message}"
        self.save()
        return self.whatsapp_link


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, verbose_name='اسم المنتج')
    quantity = models.PositiveIntegerField(default=1, verbose_name='الكمية')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')

    class Meta:
        verbose_name = 'عنصر في الطلب'
        verbose_name_plural = 'عناصر الطلبات'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self):
        """إجمالي سعر هذا المنتج في الطلب"""
        price = self.price or 0
        quantity = self.quantity or 0
        return price * quantity