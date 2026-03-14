# orders/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .serializers import (
    CartSerializer, AddToCartSerializer, UpdateCartQuantitySerializer,
    RemoveFromCartSerializer, OrderSerializer, CreateOrderSerializer
)


def get_or_create_cart(request):
    """دالة مساعدة للحصول على السلة أو إنشائها"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartAPIView(APIView):
    """
    GET: عرض السلة
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'cart': serializer.data
        })

class AddToCartAPIView(APIView):
    """POST: إضافة منتج للسلة"""
    permission_classes = [AllowAny]

    def post(self, request):
        # طباعة البيانات المستلمة للتحقق
        print("=" * 50)
        print("Request Data:", request.data)
        print("Request Body:", request.body)
        print("=" * 50)
        
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # طباعة الأخطاء
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
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

            cart_serializer = CartSerializer(cart)
            
            return Response({
                'success': True,
                'message': 'تم إضافة المنتج للسلة',
                'cart': cart_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Exception:", str(e))  # طباعة الخطأ
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UpdateCartQuantityAPIView(APIView):
    """
    PUT: تحديث كمية منتج في السلة
    """
    permission_classes = [AllowAny]

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
    """
    DELETE: حذف منتج من السلة
    """
    permission_classes = [AllowAny]

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
    """
    POST: تفريغ السلة
    """
    permission_classes = [AllowAny]

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
    """
    POST: إنشاء طلب من السلة
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = get_or_create_cart(request)
            
            if not cart.items.exists():
                return Response({
                    'success': False,
                    'message': 'السلة فارغة'
                }, status=status.HTTP_400_BAD_REQUEST)

            # إنشاء الطلب
            order = Order.objects.create(
                user=request.user,
                full_name=serializer.validated_data.get('full_name', request.user.full_name),
                phone=serializer.validated_data.get('phone', request.user.phone),
                email=serializer.validated_data.get('email', request.user.email or ''),
                address=serializer.validated_data.get('address', ''),
                notes=serializer.validated_data.get('notes', ''),
                total_amount=cart.total_price
            )

            # إضافة المنتجات للطلب
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    price=cart_item.product.final_price
                )

            # توليد رابط الواتساب
            whatsapp_link = order.generate_whatsapp_link()
            
            # تفريغ السلة
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
    """
    GET: عرض طلبات المستخدم
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'orders': serializer.data
        })


class OrderDetailAPIView(APIView):
    """
    GET: عرض تفاصيل طلب معين
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        serializer = OrderSerializer(order)
        
        return Response({
            'success': True,
            'order': serializer.data
        })