from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact, Newsletter

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and phone and subject and message:
            try:
                Contact.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    subject=subject,
                    message=message
                )
                messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً!')
                return redirect('contact:contact')
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء إرسال الرسالة: {str(e)}')
        else:
            messages.error(request, 'الرجاء ملء جميع الحقول المطلوبة')
    
    return render(request, 'contact/contact.html')


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            if Newsletter.objects.filter(email=email).exists():
                messages.warning(request, 'هذا البريد مشترك بالفعل في النشرة البريدية')
            else:
                try:
                    Newsletter.objects.create(email=email)
                    messages.success(request, 'تم الاشتراك في النشرة البريدية بنجاح!')
                except Exception as e:
                    messages.error(request, f'حدث خطأ أثناء الاشتراك: {str(e)}')
        else:
            messages.error(request, 'الرجاء إدخال البريد الإلكتروني')
        
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    return redirect('index')