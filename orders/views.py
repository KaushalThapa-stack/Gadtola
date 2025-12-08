from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


 


def place_order(request, total=0, quantity=0):
    current_user = request.user


    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2* total)/100
    grand_total = tax + total



    if request.method =='POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number  = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            order.is_ordered = True
            order.status = 'Accepted'
            order.save()

            cart_items = CartItem.objects.filter(user=current_user)
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.phone = order.phone
                orderproduct.save()

                product_variation = item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            CartItem.objects.filter(user=current_user).delete()

            mail_subject = 'Thankyou for your order!'
            message = render_to_string('orders/order_recived_email.html',{
                'user' : request.user,
                'order' : order,
            })
            to_email = order.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect('order_complete', secure_token=order.secure_token)
    else:
        return redirect('carts:checkout')


            

            
def order_complete(request, secure_token=None):
    """Order complete view using secure token for security"""
    if secure_token:
        try:
            order = Order.objects.get(secure_token=secure_token, is_ordered=True)
        except Order.DoesNotExist:
            return redirect('store')
    else:
        # Fallback to old method for backward compatibility (will be removed later)
        order_number = request.GET.get('order_number')
        transID = request.GET.get('payment_id')
        if not order_number or not transID:
            return redirect('store')
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
        except Order.DoesNotExist:
            return redirect('store')
    
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    
    subtotal = 0
    for item in ordered_products:
        subtotal += item.product_price * item.quantity
    
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'subtotal': subtotal,
    }
    return render(request, 'orders/order_complete.html', context)


def order_complete_old(request):
    """Old order complete view for backward compatibility - will be deprecated"""
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        for item in ordered_products:
            subtotal += item.product_price * item.quantity
        payment = Payment.objects.get(payment_id=transID)
        
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')


def track_order(request, tracking_id):
    """Order tracking page using 10-character tracking ID"""
    try:
        order = Order.objects.get(tracking_id=tracking_id, is_ordered=True)
    except Order.DoesNotExist:
        return render(request, 'orders/order_tracking.html', {'error': 'Order not found'})
    
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    
    subtotal = 0
    for item in ordered_products:
        subtotal += item.product_price * item.quantity
    
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'subtotal': subtotal,
        'tracking_id': tracking_id,
    }
    return render(request, 'orders/order_tracking.html', context)
            

            
