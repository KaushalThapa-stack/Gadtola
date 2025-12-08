from django.shortcuts import render
import random
from store.models import Product
from slider.models import SliderImage

def home(request):
    all_products = list(Product.objects.all().filter(is_available = True))
    products = random.sample(all_products, min(len(all_products), 12))
    # Only include slider images with existing files to avoid blank slides
    valid_slider_images = []
    for si in SliderImage.objects.all():
        try:
            if si.image and si.image.name and si.image.storage.exists(si.image.name):
                valid_slider_images.append(si)
        except Exception:
            # Skip any entries that error while checking storage
            continue
    slider_images = valid_slider_images[:5]

    context = {
        'products' : products,
        'slider_images': slider_images,
    }

    return render (request, 'home.html',context)


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


def search_page(request):
    return render(request, 'search_page.html')


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)
