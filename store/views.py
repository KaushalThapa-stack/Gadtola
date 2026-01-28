
from unicodedata import category
from django.shortcuts import get_object_or_404, render, redirect
from category.models import Category
from .models import Product, ReviewRating
from django.http import HttpResponse
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from .form import ReviewForm
from django.contrib import messages


# Create your views here.

for product in Product.objects.all():
    product.display_features = [f for f in [product.feature1, product.feature2, product.feature3, product.feature4, product.feature5] if f][:3]


def store(request, category_slug=None):
    categories = None
    parducts = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    """Product detail page with WhatsApp ordering capability"""
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    # Initialize variables
    reviews = None
    
    # GET reviews (no user auth needed)
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    # Get 5 random products (excluding current product)
    import random
    all_products = list(Product.objects.filter(is_available=True).exclude(id=single_product.id))
    random_products = random.sample(all_products, min(len(all_products), 5))
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews,
        'random_products': random_products,
    }
    return render(request, 'store/product_detail.html', context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(discription__icontains=keyword) |
                Q(product_name__icontains=keyword) |
                Q(category__category_name__icontains=keyword)
            )
            product_count = products.count()
    
    # Create product_ratings dictionary
    product_ratings = {}
    for product in products:
        reviews = ReviewRating.objects.filter(product=product, status=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            review_count = reviews.count()
            product_ratings[product.id] = {
                'avg_rating': avg_rating,
                'review_count': review_count
            }
    
    context = {
        'products': products,
        'product_count': product_count,
        'product_ratings': product_ratings,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    """Submit product review (no authentication required)"""
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = ReviewRating()
            data.subject = form.cleaned_data['subject']
            data.review = form.cleaned_data['review']
            data.rating = form.cleaned_data['rating']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            # No user_id since we're not using authentication
            data.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect(url)

