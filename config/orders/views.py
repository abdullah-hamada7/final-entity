from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden
from offers.models import Offer, OfferProduct 
import json


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': 'تم إضافة المنتج للسلة',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


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
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', request.user.full_name),
            phone=request.POST.get('phone', request.user.phone),
            email=request.POST.get('email', request.user.email or ''),
            address=request.POST.get('address', ''),
            notes=request.POST.get('notes', ''),
            total_amount=cart.total_price
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.final_price
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



def add_all_offer_products(request, offer_id):
    if request.method == "POST":
        data = json.loads(request.body)
        products_data = data.get("products", [])
        cart, created = Cart.objects.get_or_create(user=request.user)

        added_products = []

        for p in products_data:
            product = Product.objects.get(id=p["id"])
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            added_products.append({
                "id": product.id,
                "name": product.name,
                "price": product.final_price
            })

        return JsonResponse({
            "status": "success",
            "cart_count": cart.items.count(),
            "products": added_products
        })
        
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
            'price': float(ci.product.final_price),
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

        # Create order
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', request.user.full_name),
            phone=request.POST.get('phone', request.user.phone),
            email=request.POST.get('email', request.user.email or ''),
            address=request.POST.get('address', ''),
            notes=request.POST.get('notes', ''),
            total_amount=cart.total_price
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.final_price
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
    
    


@csrf_exempt
def submit_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            items = data.get("items", [])

            if not items:
                return JsonResponse({"success": False, "message": "السلة فارغة"}, status=400)

            user = None
            if request.user.is_authenticated:
                user = request.user

            # إنشاء الطلب
            order = Order.objects.create(
                user=user,
                total_amount=sum([float(item.get("price", 0)) * int(item.get("quantity", 1)) for item in items])
            )

            # إضافة المنتجات
            for item in items:
                product_id = item.get("product_id")
                product_name = item.get("name")
                quantity = int(item.get("quantity", 1))
                price = float(item.get("price", 0))

                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,  # لو المنتج موجود في الـ DB
                    product_name=product_name,
                    quantity=quantity,
                    price=price
                )

            # مسح السلة
            if user:
                Cart.objects.filter(user=user).delete()
            else:
                session_key = request.session.session_key
                if session_key:
                    Cart.objects.filter(session_key=session_key).delete()

            return JsonResponse({"success": True, "message": "تم تسجيل الطلب بنجاح ✅"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "طريقة الطلب غير صحيحة"}, status=405)