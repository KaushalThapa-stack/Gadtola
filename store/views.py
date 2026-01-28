
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse

from category.models import Category, ChildCategory, ParentCategory
from .models import Product, ReviewRating
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from .form import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


def store(request, parent_slug=None, child_slug=None, slug=None):
    """
    Store view supporting parent and child category filtering
    parent_slug: outfit, shoes, or combos
    child_slug: specific child category slug
    slug: legacy category slug (backward compatibility)
    """
    products = Product.objects.filter(is_available=True)
    parent_category = None
    child_category = None
    child_categories_list = []
    
    # Handle legacy category slug
    if slug:
        try:
            category = Category.objects.get(slug=slug)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass
    
    if parent_slug:
        try:
            parent_category = ParentCategory.objects.get(slug=parent_slug)
            # Filter products by parent category
            products = products.filter(child_category__parent=parent_category)
            # Get all child categories under this parent
            child_categories_list = parent_category.children.all()
            
            if child_slug:
                try:
                    child_category = ChildCategory.objects.get(slug=child_slug, parent=parent_category)
                    # Further filter by child category
                    products = products.filter(child_category=child_category)
                except ChildCategory.DoesNotExist:
                    pass
        except ParentCategory.DoesNotExist:
            pass
    
    # Pagination
    paginator = Paginator(products.order_by('-created_date'), 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
    
    context = {
        'products': paged_products,
        'product_count': product_count,
        'parent_category': parent_category,
        'child_category': child_category,
        'child_categories': child_categories_list,
        'parent_slug': parent_slug,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, parent_slug, product_slug):
    """Product detail view with combo size support"""
    try:
        parent_category = ParentCategory.objects.get(slug=parent_slug)
        single_product = Product.objects.get(
            child_category__parent=parent_category,
            slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request),
            product=single_product
        ).exists()
    except (ParentCategory.DoesNotExist, Product.DoesNotExist):
        raise

    # Check if product is in user's orders
    orderproduct = None
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user,
                product_id=single_product.id
            ).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    
    # Get reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    # Get random products for "You may also like"
    import random
    all_products = list(Product.objects.filter(is_available=True).exclude(id=single_product.id))
    random_products = random.sample(all_products, min(len(all_products), 5))
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'random_products': random_products,
    }
    
    return render(request, 'store/product_detail.html', context)


def search(request):
    """Search products"""
    products = Product.objects.filter(is_available=True)
    product_count = 0
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = products.filter(
                Q(discription__icontains=keyword) |
                Q(product_name__icontains=keyword) |
                Q(child_category__name__icontains=keyword)
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
    """Submit or update a product review"""
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
