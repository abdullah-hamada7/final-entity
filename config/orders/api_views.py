# orders/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CartItem, Order, OrderItem
from products.models import Product
from .pricing import get_product_unit_price, resolve_cart_item_unit_price
from .utils import get_or_create_cart, build_order_fields_from_user
from .serializers import (
    CartSerializer, AddToCartSerializer, UpdateCartQuantitySerializer,
    RemoveFromCartSerializer, OrderSerializer, CreateOrderSerializer
)


class CartAPIView(APIView):
    """GET: عرض السلة"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'cart': serializer.data
        })


class AddToCartAPIView(APIView):
    """POST: إضافة منتج للسلة"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        offer_id = serializer.validated_data.get('offer_id')

        try:
            product = get_object_or_404(Product, id=product_id, is_active=True)
            cart = get_or_create_cart(request)
            unit_price = get_product_unit_price(product, offer_id)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'unit_price': unit_price}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.unit_price = resolve_cart_item_unit_price(cart_item, offer_id)
                cart_item.save()

            cart_serializer = CartSerializer(cart)

            return Response({
                'success': True,
                'message': 'تم إضافة المنتج للسلة',
                'cart': cart_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCartQuantityAPIView(APIView):
    """PUT: تحديث كمية منتج في السلة"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateCartQuantitySerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        item_id = serializer.validated_data['item_id']
        quantity = serializer.validated_data['quantity']

        try:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                item_subtotal = float(cart_item.subtotal)
            else:
                cart_item.delete()
                item_subtotal = 0

            cart_serializer = CartSerializer(cart)

            return Response({
                'success': True,
                'message': 'تم تحديث الكمية',
                'item_subtotal': item_subtotal,
                'cart': cart_serializer.data
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveFromCartAPIView(APIView):
    """DELETE: حذف منتج من السلة"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        item_id = serializer.validated_data['item_id']

        try:
            cart = get_or_create_cart(request)
            CartItem.objects.filter(id=item_id, cart=cart).delete()

            cart_serializer = CartSerializer(cart)

            return Response({
                'success': True,
                'message': 'تم حذف المنتج',
                'cart': cart_serializer.data
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClearCartAPIView(APIView):
    """POST: تفريغ السلة"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = get_or_create_cart(request)
            cart.items.all().delete()

            return Response({
                'success': True,
                'message': 'تم تفريغ السلة بنجاح',
                'cart_count': 0,
                'cart_total': 0.0
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateOrderAPIView(APIView):
    """POST: إنشاء طلب من السلة"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_error = None
            for value in errors.values():
                if isinstance(value, list) and value:
                    first_error = value[0]
                    break
                if isinstance(value, str):
                    first_error = value
                    break
            return Response({
                'success': False,
                'message': first_error or 'بيانات الطلب غير صالحة',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = get_or_create_cart(request)

            if not cart.items.exists():
                return Response({
                    'success': False,
                    'message': 'السلة فارغة'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            order_fields = build_order_fields_from_user(
                user,
                serializer.validated_data.get('notes', ''),
            )

            order = Order.objects.create(
                user=user,
                total_amount=cart.total_price,
                **order_fields,
            )

            for cart_item in cart.items.select_related('product'):
                product = cart_item.product
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.effective_price
                )

            whatsapp_link = order.generate_whatsapp_link()
            cart.items.all().delete()

            order_serializer = OrderSerializer(order)

            return Response({
                'success': True,
                'message': 'تم إنشاء الطلب بنجاح',
                'order': order_serializer.data,
                'whatsapp_link': whatsapp_link
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderListAPIView(APIView):
    """GET: عرض طلبات المستخدم"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)

        return Response({
            'success': True,
            'orders': serializer.data
        })


class OrderDetailAPIView(APIView):
    """GET: عرض تفاصيل طلب معين"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        serializer = OrderSerializer(order)

        return Response({
            'success': True,
            'order': serializer.data
        })
