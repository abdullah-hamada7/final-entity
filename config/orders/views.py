from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .pricing import get_product_unit_price, resolve_cart_item_unit_price
from .utils import get_or_create_cart, build_order_fields_from_user
import json
from offers.models import Offer, OfferProduct


@login_required
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        unit_price = get_product_unit_price(product)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'unit_price': unit_price}
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.unit_price is None:
                cart_item.unit_price = unit_price
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': 'تم إضافة المنتج للسلة',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        cart = get_or_create_cart(request)
        CartItem.objects.filter(id=item_id, cart=cart).delete()

        return JsonResponse({
            'success': True,
            'message': 'تم حذف المنتج',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def update_cart_quantity(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity'))

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        return JsonResponse({
            'success': True,
            'item_subtotal': float(cart_item.subtotal) if quantity > 0 else 0,
            'cart_total': float(cart.total_price)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def clear_cart(request):
    try:
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return JsonResponse({
            'success': True,
            'message': 'تم تفريغ السلة بنجاح',
            'cart_count': 0,
            'cart_total': 0.0
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
def cart_view(request):
    cart = get_or_create_cart(request)
    context = {'cart': cart}
    return render(request, 'orders/cart.html', context)


@login_required
def checkout(request):
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, 'السلة فارغة')
        return redirect('products:list')

    if request.method == 'POST':
        order_fields = build_order_fields_from_user(
            request.user,
            request.POST.get('notes', ''),
        )
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            **order_fields,
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.effective_price
            )

        whatsapp_link = order.generate_whatsapp_link()

        cart.items.all().delete()

        messages.success(request, 'تم إنشاء الطلب بنجاح')

        return redirect(whatsapp_link)

    context = {'cart': cart}
    return render(request, 'orders/checkout.html', context)


@login_required
def order_list(request):
    """Display user's orders"""
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_number):
    """Display order details"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)



@login_required
def add_all_offer_products(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, id=offer_id, is_active=True)
        cart = get_or_create_cart(request)

        added_products = []
        offer_products = OfferProduct.objects.filter(offer=offer).select_related('product')

        for offer_product in offer_products:
            product = offer_product.product
            if not product.is_active:
                continue

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

            added_products.append({
                "id": product.id,
                "name": product.name,
                "price": float(unit_price),
            })

        return JsonResponse({
            "status": "success",
            "cart_count": cart.items.count(),
            "products": added_products
        })
        
@login_required
def cart_api(request):
    """Return cart JSON (items, totals). GET only."""
    cart = get_or_create_cart(request)
    items = []
    for ci in cart.items.all():
        items.append({
            'cart_item_id': ci.id,
            'product_id': ci.product.id,
            'name': ci.product.name,
            'quantity': ci.quantity,
            'price': float(ci.effective_price),
            'subtotal': float(ci.subtotal),
            'is_active': ci.product.is_active,
            'slug': getattr(ci.product, 'slug', ''),
        })

    return JsonResponse({
        'success': True,
        'items': items,
        'cart_count': cart.total_items,
        'cart_total': float(cart.total_price)
    })


@login_required
@require_POST
def api_create_order(request):
    """
    Create an Order from the current cart (AJAX).
    Returns JSON with success and whatsapp_link + order_number.
    """
    try:
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return JsonResponse({'success': False, 'message': 'السلة فارغة'}, status=400)

        order_fields = build_order_fields_from_user(
            request.user,
            request.POST.get('notes', ''),
        )
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            **order_fields,
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.effective_price
            )

        # Generate whatsapp link and clear cart
        whatsapp_link = order.generate_whatsapp_link()
        cart.items.all().delete()

        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء الطلب بنجاح',
            'whatsapp_link': whatsapp_link,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    


@login_required
@require_POST
def submit_cart(request):
    try:
        data = json.loads(request.body or '{}')
        db_cart = get_or_create_cart(request)
        user = request.user

        if not db_cart.items.exists():
            return JsonResponse({"success": False, "message": "السلة فارغة"}, status=400)

        order_fields = build_order_fields_from_user(user, data.get('notes', ''))

        order = Order.objects.create(
            user=user,
            total_amount=db_cart.total_price,
            **order_fields,
        )

        for cart_item in db_cart.items.select_related('product'):
            product = cart_item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=cart_item.quantity,
                price=cart_item.effective_price,
            )

        whatsapp_link = order.generate_whatsapp_link()
        db_cart.items.all().delete()

        return JsonResponse({
            "success": True,
            "message": "تم تسجيل الطلب بنجاح",
            "whatsapp_link": whatsapp_link,
            "order_number": order.order_number,
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "بيانات غير صالحة"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)