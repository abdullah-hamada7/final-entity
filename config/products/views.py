from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, F, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Product, Review
from .utils import build_products_query

PRODUCTS_PER_PAGE = 12
FILTER_CATEGORIES_LIMIT = 3


def active_products_queryset():
    return (
        Product.objects.filter(is_active=True)
        .select_related('category', 'brand')
        .prefetch_related('images')
    )


def paginate_queryset(request, queryset):
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    categories = Category.objects.filter(is_active=True)[:6]
    return render(request, 'index.html', {
        'featured_products': featured_products,
        'categories': categories
    })


def products_list(request):
    categories = Category.objects.filter(is_active=True)
    filter_categories = categories.order_by('order', 'name')[:FILTER_CATEGORIES_LIMIT]
    products = active_products_queryset()

    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    valid_slugs = set(categories.values_list('slug', flat=True))

    if category_filter and category_filter not in valid_slugs:
        category_filter = ''
    elif category_filter:
        products = products.filter(category__slug=category_filter)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    page_obj = paginate_queryset(request, products)
    active_category = None
    if category_filter:
        active_category = categories.filter(slug=category_filter).first()

    context = {
        'categories': categories,
        'filter_categories': filter_categories,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'active_category': active_category,
        'query_params': build_products_query(search_query, category_filter),
    }
    return render(request, 'products/products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('images', 'features'),
        slug=slug,
        is_active=True,
    )

    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
    product.views += 1

    related_products = active_products_queryset().filter(
        category=product.category,
    ).exclude(id=product.id)[:4]

    reviews = product.reviews.select_related('user').all()[:20]
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()

    rating_stats = product.reviews.aggregate(avg=Avg('rating'))
    avg_rating = rating_stats['avg']

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': avg_rating,
        'review_count': product.reviews.count(),
    }
    return render(request, 'products/product_details.html', context)


def category_products(request, slug):
    """Display products by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = active_products_queryset().filter(category=category)

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    page_obj = paginate_queryset(request, products)

    context = {
        'category': category,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'query_params': build_products_query(search_query),
    }

    return render(request, 'products/category.html', context)


def add_review(request, product_id):
    """Add review to a product"""
    wants_json = 'application/json' in request.headers.get('Accept', '')

    if not request.user.is_authenticated:
        if wants_json:
            return JsonResponse(
                {'success': False, 'message': 'يجب تسجيل الدخول لإضافة تقييم'},
                status=401,
            )
        messages.error(request, 'يجب تسجيل الدخول لإضافة تقييم')
        return redirect('users:login')

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating_raw = request.POST.get('rating')
        comment = (request.POST.get('comment') or '').strip()

        try:
            rating = int(rating_raw)
        except (TypeError, ValueError):
            if wants_json:
                return JsonResponse({'success': False, 'message': 'التقييم غير صالح'}, status=400)
            messages.error(request, 'التقييم غير صالح')
            return redirect('products:detail', slug=product.slug)

        if rating < 1 or rating > 5:
            if wants_json:
                return JsonResponse({'success': False, 'message': 'التقييم يجب أن يكون بين 1 و 5'}, status=400)
            messages.error(request, 'التقييم يجب أن يكون بين 1 و 5')
            return redirect('products:detail', slug=product.slug)

        if len(comment) < 3:
            if wants_json:
                return JsonResponse({'success': False, 'message': 'التعليق قصير جدًا'}, status=400)
            messages.error(request, 'التعليق قصير جدًا')
            return redirect('products:detail', slug=product.slug)

        if len(comment) > 1000:
            if wants_json:
                return JsonResponse({'success': False, 'message': 'التعليق طويل جدًا'}, status=400)
            messages.error(request, 'التعليق طويل جدًا')
            return redirect('products:detail', slug=product.slug)

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )

        if wants_json:
            return JsonResponse({'success': True, 'message': 'تم إرسال التقييم بنجاح'})

        messages.success(request, 'تم إضافة التقييم بنجاح')
        return redirect('products:detail', slug=product.slug)

    return redirect('products:home')
