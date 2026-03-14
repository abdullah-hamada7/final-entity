from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'كلمة المرور غير متطابقة')
            return render(request, 'users/register.html')
        
        if CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'رقم الهاتف مسجل مسبقاً')
            return render(request, 'users/register.html')
        
        user = CustomUser.objects.create_user(
            phone=phone,
            password=password,
            full_name=full_name,
            email=email
        )
        
        login(request, user)
        messages.success(request, 'تم إنشاء الحساب بنجاح')
        return redirect('home')
    
    return render(request, 'users/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        user = authenticate(request, phone=phone, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'تم تسجيل الدخول بنجاح')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'رقم الهاتف أو كلمة المرور غير صحيحة')
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.full_name = request.POST.get('full_name', user.full_name)
        user.email = request.POST.get('email', user.email)
        
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html')


def reset_password_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'كلمة المرور غير متطابقة')
            return render(request, 'users/reset_password.html')

        try:
            user = CustomUser.objects.get(phone=phone)
            user.set_password(password)
            user.save()
            messages.success(request, 'تم تغيير كلمة المرور بنجاح')
            return redirect('users:login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'رقم الهاتف غير موجود')
    
    return render(request, 'users/reset_password.html')