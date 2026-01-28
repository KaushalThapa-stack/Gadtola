"""
WhatsApp Message Builder Utility for Session-Based Ordering
Generates WhatsApp URLs with prefilled product/order messages
"""

from urllib.parse import quote
from django.conf import settings
from django.template.loader import render_to_string


# Owner's WhatsApp number (configure in settings or here)
OWNER_WHATSAPP_NUMBER = getattr(settings, 'OWNER_WHATSAPP_NUMBER', '919876543210')


def get_whatsapp_url(message_text):
    """
    Convert a message into a WhatsApp chat URL
    
    Args:
        message_text (str): The message to send
        
    Returns:
        str: WhatsApp URL ready for opening
    """
    encoded_message = quote(message_text)
    return f"https://wa.me/{OWNER_WHATSAPP_NUMBER}?text={encoded_message}"


def build_product_message(product, quantity, variations=None, price=None, image_url=None):
    """
    Build a WhatsApp message for a single product
    
    Args:
        product: Product model instance
        quantity: Number of items
        variations: List of Variation model instances
        price: Product price (default uses product.price)
        image_url: Full URL to product image
        
    Returns:
        str: Formatted WhatsApp message
    """
    if price is None:
        price = product.price
    
    total_price = price * quantity
    
    # Build variation string
    variation_str = ""
    if variations:
        variation_str = "\n"
        for var in variations:
            variation_str += f"• {var.variation_category.title()}: {var.variation_value}\n"
    
    message = f"""📦 *Product Order*

*{product.product_name}*
{variation_str}
Quantity: {quantity}
Price per item: Rs. {price}
Total: Rs. {total_price}

{image_url if image_url else ''}
"""
    return message.strip()


def build_cart_message(cart_items_data, grand_total=0):
    """
    Build a WhatsApp message for entire cart
    
    Args:
        cart_items_data: List of dicts with product, quantity, variations, price, image_url
        grand_total: Final total (no tax)
        
    Returns:
        str: Formatted WhatsApp message with full cart details
    """
    message = "Order Summary\n\n"
    
    for idx, item in enumerate(cart_items_data, 1):
        product = item['product']
        quantity = item['quantity']
        variations = item.get('variations', [])
        price = item.get('price', product.price)
        total_item = price * quantity
        
        # Add product name and image
        message += f"{idx}. {product.product_name}\n"
        
        # Add variations if any
        if variations:
            for var in variations:
                message += f"   - {var.variation_category.title()}: {var.variation_value}\n"
        
        message += f"   Qty: {quantity} x Rs.{price} = Rs.{total_item}\n\n"
    
    # Add totals
    message += f"─────────────────\n"
    message += f"Total: Rs. {grand_total}\n\n"
    message += "Please confirm this order and let us know your delivery address. Thanks!"
    
    return message.strip()


def get_product_whatsapp_link(product, quantity, variations=None, price=None, image_url=None):
    """
    Get complete WhatsApp chat link for a product
    
    Args:
        product: Product model instance
        quantity: Number of items
        variations: List of Variation instances
        price: Product price
        image_url: Full URL to product image
        
    Returns:
        str: Complete WhatsApp URL
    """
    message = build_product_message(product, quantity, variations, price, image_url)
    return get_whatsapp_url(message)


def get_cart_whatsapp_link(cart_items_data, grand_total=0):
    """
    Get complete WhatsApp chat link for entire cart
    
    Args:
        cart_items_data: List of cart item dicts
        grand_total: Total (no tax)
        
    Returns:
        str: Complete WhatsApp URL
    """
    message = build_cart_message(cart_items_data, grand_total)
    return get_whatsapp_url(message)
