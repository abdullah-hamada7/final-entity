from .models import Cart


def get_or_create_cart(request):
    """Return the authenticated user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return cart


def build_order_fields_from_user(user, notes=''):
    """Snapshot contact details from the registered user at checkout time."""
    return {
        'full_name': user.full_name,
        'phone': user.phone,
        'email': user.email or '',
        'address': '',
        'notes': (notes or '').strip(),
    }
