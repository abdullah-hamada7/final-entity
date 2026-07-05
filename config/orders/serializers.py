# orders/serializers.py
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Serializer بسيط للمنتج"""
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'final_price', 'icon', 'is_active']

    def get_final_price(self, obj):
        return obj.final_price


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer لعناصر السلة"""
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'effective_price', 'subtotal']


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
    product_id = serializers.IntegerField(error_messages={
        'invalid': 'معرف المنتج غير صالح',
        'required': 'معرف المنتج مطلوب',
    })
    quantity = serializers.IntegerField(default=1, min_value=1, error_messages={
        'invalid': 'الكمية غير صالحة',
        'min_value': 'الكمية يجب أن تكون 1 على الأقل',
    })
    offer_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_product_id(self, value):
        try:
            product_id = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError('معرف المنتج غير صالح')
        if not Product.objects.filter(id=product_id, is_active=True).exists():
            raise serializers.ValidationError('المنتج غير موجود أو غير متاح')
        return product_id

    def validate(self, attrs):
        offer_id = attrs.get('offer_id')
        if not offer_id:
            return attrs

        from offers.models import Offer, OfferProduct

        try:
            offer = Offer.objects.get(id=offer_id, is_active=True)
        except Offer.DoesNotExist:
            raise serializers.ValidationError({'offer_id': 'العرض غير موجود'})

        if not offer.is_valid():
            raise serializers.ValidationError({'offer_id': 'العرض غير متاح حالياً'})

        if not OfferProduct.objects.filter(offer=offer, product_id=attrs['product_id']).exists():
            raise serializers.ValidationError({'offer_id': 'المنتج غير مشمول في هذا العرض'})

        return attrs


class UpdateCartQuantitySerializer(serializers.Serializer):
    """Serializer لتحديث كمية المنتج في السلة"""
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)


class RemoveFromCartSerializer(serializers.Serializer):
    """Serializer لحذف منتج من السلة"""
    item_id = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer لعناصر الطلب"""
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """Serializer للطلبات"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'full_name', 'phone', 'email',
            'address', 'notes', 'total_amount', 'status', 'status_display', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'status', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer لإنشاء طلب جديد — ملاحظات اختيارية فقط."""
    notes = serializers.CharField(required=False, allow_blank=True, max_length=2000)
