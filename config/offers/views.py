from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.models import Category, Product
from .models import Offer, OfferProduct
from .utils import build_offers_query
import json
from orders.models import Cart, CartItem
from orders.pricing import get_product_unit_price, resolve_cart_item_unit_price

OFFERS_PER_PAGE = 9


def paginate_offers(request, queryset):
    paginator = Paginator(queryset, OFFERS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def offers_list(request):
    now = timezone.now()
    offers = Offer.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products__product').order_by('-start_date')

    category_slug = (request.GET.get('category') or '').strip()
    search_query = (request.GET.get('search') or '').strip()

    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            offers = offers.filter(products__product__category=category).distinct()
        except Category.DoesNotExist:
            messages.warning(request, 'الفئة المحددة غير موجودة')
            category_slug = ''

    if search_query:
        offers = offers.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(products__product__name__icontains=search_query)
        ).distinct()

    page_obj = paginate_offers(request, offers)
    categories = Category.objects.filter(is_active=True)

    context = {
        'offers': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'query_params': build_offers_query(search_query, category_slug),
    }
    return render(request, 'offers/offers.html', context)


def offer_detail(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, is_active=True)

    now = timezone.now()
    if not (offer.start_date <= now <= offer.end_date):
        messages.warning(request, 'هذا العرض غير متاح حالياً')
        return redirect('offers:list')

    offer_products = OfferProduct.objects.filter(offer=offer).select_related('product')

    context = {
        'offer': offer,
        'offer_products': offer_products,
    }
    return render(request, 'offers/offer_detail.html', context)


@require_POST
def apply_offer_to_cart(request):
    try:
        data = json.loads(request.body)
        offer_id = data.get('offer_id')

        offer = get_object_or_404(Offer, id=offer_id, is_active=True)
        if not offer.is_valid():
            return JsonResponse({'success': False, 'message': 'العرض غير متاح'}, status=400)

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        offer_products = OfferProduct.objects.filter(offer=offer).select_related('product')
        added_products = []

        for offer_product in offer_products:
            product = offer_product.product
            if product.is_active and product.stock > 0:
                unit_price = offer_product.get_offer_price()
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': 1, 'unit_price': unit_price}
                )
                if not created:
                    cart_item.quantity += 1
                    cart_item.unit_price = resolve_cart_item_unit_price(cart_item, offer.id)
                    cart_item.save()
                added_products.append(product.name)

        if added_products:
            return JsonResponse({
                'success': True,
                'message': f'تم إضافة {len(added_products)} منتجات إلى السلة',
                'cart_count': cart.total_items,
                'cart_total': float(cart.total_price)
            })
        return JsonResponse({
            'success': False,
            'message': 'لا توجد منتجات متاحة في هذا العرض'
        }, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
