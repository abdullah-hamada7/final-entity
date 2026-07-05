from decimal import Decimal

from offers.models import Offer, OfferProduct


def get_product_unit_price(product, offer_id=None):
    """Return the effective unit price for a product, optionally from an active offer."""
    if offer_id:
        try:
            offer = Offer.objects.get(id=offer_id, is_active=True)
            if offer.is_valid():
                offer_product = OfferProduct.objects.get(offer=offer, product=product)
                return offer_product.get_offer_price()
        except (Offer.DoesNotExist, OfferProduct.DoesNotExist):
            pass

    final_price = getattr(product, 'final_price', None)
    if final_price is not None:
        return final_price
    return Decimal(product.price or 0)


def resolve_cart_item_unit_price(cart_item, offer_id=None):
    """Pick the best stored unit price when adding or updating a cart item."""
    new_price = get_product_unit_price(cart_item.product, offer_id)

    if cart_item.unit_price is None:
        return new_price

    if offer_id and new_price < cart_item.unit_price:
        return new_price

    return cart_item.unit_price
