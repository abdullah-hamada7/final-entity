# orders/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Serializer بسيط للمنتج"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'final_price', 'is_active']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer لعناصر السلة"""
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    """Serializer للسلة"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer لإضافة منتج للسلة"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("المنتج غير موجود أو غير متاح")
        return value


class UpdateCartQuantitySerializer(serializers.Serializer):
    """Serializer لتحديث كمية المنتج في السلة"""
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)


class RemoveFromCartSerializer(serializers.Serializer):
    """Serializer لحذف منتج من السلة"""
    item_id = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer لعناصر الطلب"""
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer للطلبات"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'full_name', 'phone', 'email',
            'address', 'notes', 'total_amount', 'status', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'status', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer لإنشاء طلب جديد"""
    full_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)
    address = serializers.CharField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)