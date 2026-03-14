from django.db import models
from django.utils import timezone

class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('استفسار عن منتج', 'استفسار عن منتج'),
        ('طلب عرض سعر', 'طلب عرض سعر'),
        ('دعم فني', 'دعم فني'),
        ('شكوى أو اقتراح', 'شكوى أو اقتراح'),
        ('أخرى', 'أخرى'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('in_progress', 'قيد المعالجة'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='الاسم الكامل')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, verbose_name='الموضوع')
    message = models.TextField(verbose_name='الرسالة')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='الحالة')
    admin_notes = models.TextField(blank=True, verbose_name='ملاحظات الإدارة')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإرسال')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Newsletter(models.Model):
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    subscribed_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الاشتراك')
    
    class Meta:
        verbose_name = 'مشترك في النشرة البريدية'
        verbose_name_plural = 'المشتركون في النشرة البريدية'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class Notification(models.Model):
    title = models.CharField(max_length=255, verbose_name='العنوان')
    message = models.TextField(verbose_name='الرسالة')
    notification_type = models.CharField(max_length=50, default='info', verbose_name='النوع')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title