from .models import Cart, CartItem
from .views import _cart_id


def counter(request):
    """
    Context processor to add cart count to all templates
    Now session-based only (no user authentication)
    """
    cart_count = 0
    
    # Skip admin pages
    if 'admin' in request.path:
        return {}
    
    try:
        # Get cart items from session only
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        cart_items = CartItem.objects.all().filter(cart=cart[:1])
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0
    
    return dict(cart_count=cart_count)
