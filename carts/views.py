"""
Shopping cart views - Session-based only (no user authentication)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.db.models import Q
from django.contrib import messages
from .whatsapp_utils import get_cart_whatsapp_link, get_product_whatsapp_link


def _cart_id(request):
    """Generate or retrieve session cart ID"""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def update_cart(request, product_id, cart_item_id):
    """Update cart item quantity from direct input - Session-based only"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
            
        # Get quantity from URL parameter
        new_quantity = int(request.GET.get('qty', 1))
        if new_quantity > 0:
            max_allowed = max(0, product.stock)
            if new_quantity > max_allowed:
                new_quantity = max_allowed
                messages.warning(request, f"Only {max_allowed} items available in stock.")
            cart_item.quantity = new_quantity if new_quantity > 0 else 1
            cart_item.save()
    except Exception as e:
        pass
        
    return redirect('carts:cart')


def add_cart(request, product_id):
    """Add product to session-based cart (no authentication required)"""
    product = Product.objects.get(id=product_id)
    product_variation = []
    
    if request.method == 'POST':
        # Collect selected variations from form
        for items in request.POST:
            key = items
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    # Get or create session-based cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    # Check if product with same variations already in cart
    is_cart_item_exit = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exit:
        # Get all cart items for this product
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for item in cart_items:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            # Same variation exists - just increase quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            if item.quantity < product.stock:
                item.quantity += 1
                item.save()
            else:
                messages.warning(request, f"Cannot add more than available stock ({product.stock}).")
        else:
            # Different variation - create new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        # First time adding this product
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    
    return redirect('carts:cart')


def remove_cart(request, product_id, cart_item_id):
    """Decrease quantity of cart item by 1"""
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('carts:cart')


def remove_cart_item(request, product_id, cart_item_id):
    """Remove entire cart item from cart"""
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('carts:cart')


def cart(request, total=0, quantity=0, cart_items=None):
    """Display session-based shopping cart with WhatsApp order button"""
    try:
        total = 0
        quantity = 0
        
        # Get session-based cart items only (no user authentication)
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            cart_item.sub_total = cart_item.product.price * cart_item.quantity
            total += cart_item.sub_total
            quantity += cart_item.quantity
        grand_total = total  # No tax, subtotal = grand_total
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)



