from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Review
from django.core.paginator import Paginator

def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    categories = Category.objects.filter(is_active=True)[:6]
    return render(request, 'index.html', {
        'featured_products': featured_products,
        'categories': categories
    })
    
    
def products_list(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'categories': categories,
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'products/products.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    product.views += 1
    product.save(update_fields=['views'])
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_details.html', context)

def category_products(request, slug):
    """Display products by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
    }
    
    return render(request, 'products/category.html', context)

def add_review(request, product_id):
    """Add review to a product"""
    if not request.user.is_authenticated:
        messages.error(request, 'يجب تسجيل الدخول لإضافة تقييم')
        return redirect('users:login')
    
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        messages.success(request, 'تم إضافة التقييم بنجاح')
        return redirect('products:detail', slug=product.slug)
    
    return redirect('products:list')