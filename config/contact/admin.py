from django.contrib import admin
from .models import Contact, Newsletter, Notification

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'email', 'phone', 'subject', 'status', 'created_at']
    list_filter = ['subject', 'status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('معلومات المرسل', {
            'fields': ('name', 'email', 'phone')
        }),
        ('تفاصيل الرسالة', {
            'fields': ('subject', 'message', 'created_at', 'updated_at')
        }),
        ('إدارة الرسالة', {
            'fields': ('status', 'admin_notes')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')
    
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'تم تحديث {updated} رسالة إلى "قيد المعالجة"')
    mark_as_in_progress.short_description = 'تحديد كـ "قيد المعالجة"'
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f'تم تحديث {updated} رسالة إلى "تم الحل"')
    mark_as_resolved.short_description = 'تحديد كـ "تم الحل"'
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'تم تحديث {updated} رسالة إلى "مغلق"')
    mark_as_closed.short_description = 'تحديد كـ "مغلق"'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    list_editable = ['is_active']
    date_hierarchy = 'subscribed_at'
    list_per_page = 50
    
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} مشترك')
    activate_subscribers.short_description = 'تفعيل المشتركين'
    
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم إلغاء تفعيل {updated} مشترك')
    deactivate_subscribers.short_description = 'إلغاء تفعيل المشتركين'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    
    list_display = ['title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    list_per_page = 30
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'تم تحديد {updated} إشعار كمقروء')
    mark_as_read.short_description = 'تحديد كمقروء'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'تم تحديد {updated} إشعار كغير مقروء')
    mark_as_unread.short_description = 'تحديد كغير مقروء'