from django.db import models
from category.models import Category, ChildCategory
from django.urls import reverse
from accounts.models import Account
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='photos/brands', blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug         = models.SlugField(max_length=200, unique=True)
    discription  = models.CharField(max_length=500, blank=True)
    
    price        = models.IntegerField()
    old_price    = models.IntegerField(blank=True, null=True)  # optional

    # Images (min 2, max 5)
    image1 = models.ImageField(upload_to='photos/products',blank=True,null=True)

    image2 = models.ImageField(upload_to='photos/products',blank=True, null=True)

    image3 = models.ImageField(upload_to='photos/products', blank=True, null=True)
    image4 = models.ImageField(upload_to='photos/products', blank=True, null=True)
    image5 = models.ImageField(upload_to='photos/products', blank=True, null=True)

    # Features (min 2, max 5)
    feature1 = models.CharField(max_length=200,blank=True,null=True)
    feature2 = models.CharField(max_length=200,blank=True,null=True)
    feature3 = models.CharField(max_length=200, blank=True, null=True)
    feature4 = models.CharField(max_length=200, blank=True, null=True)
    feature5 = models.CharField(max_length=200, blank=True, null=True)

    stock        = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    child_category = models.ForeignKey(ChildCategory, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Size data for combos (stores selected size combinations)
    # Format: {'default_upper': 'S', 'default_lower': '30', 'default_shoe': '42'}
    combo_size_config = models.JSONField(default=dict, blank=True)
    
    # Product-specific selected sizes (multi-select per parent category)
    # Format: {'upper_sizes': ['S', 'M', 'L'], 'lower_sizes': ['28', '30'], 'shoe_sizes': ['39', '40']}
    selected_sizes = models.JSONField(default=dict, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_at  = models.DateTimeField(auto_now=True)

    @property
    def features(self):
        """Return max 3 non-empty features"""
        all_features = [self.feature1, self.feature2, self.feature3, self.feature4, self.feature5]
        return [f for f in all_features if f][:3]

    def get_url(self):
        if self.child_category:
            return reverse('product_detail', args=[self.child_category.parent.slug, self.slug])
        elif self.category:
            return reverse('product_detail', args=[self.category.slug, self.slug])
        return reverse('store')

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def clean(self):
        # Validate min 2 images
        if not self.image1 or not self.image2:
            raise ValidationError("At least 2 product images are required.")
        # Validate min 2 features
        if not self.feature1 or not self.feature2:
            raise ValidationError("At least 2 features are required.")

    def __str__(self):
        return self.product_name

    def is_combo(self):
        """Check if product is from Combos parent category"""
        if self.child_category:
            return self.child_category.parent.key == 'combos'
        return False

    def is_upper(self):
        """Check if product is from Upper parent category"""
        if self.child_category:
            return self.child_category.parent.key == 'upper'
        return False

    def is_lower(self):
        """Check if product is from Lower parent category"""
        if self.child_category:
            return self.child_category.parent.key == 'lower'
        return False

    def is_shoes(self):
        """Check if product is from Shoes parent category"""
        if self.child_category:
            return self.child_category.parent.key == 'shoes'
        return False

    def get_parent_category_key(self):
        """Get parent category key"""
        if self.child_category:
            return self.child_category.parent.key
        return None

    def get_available_sizes(self):
        """Get sizes available for this product (intersection of selected and category sizes)"""
        if not self.child_category:
            return []
        
        parent_key = self.child_category.parent.key
        selected = self.selected_sizes or {}
        
        if parent_key == 'upper':
            category_sizes = self.child_category.get_sizes()
            product_sizes = selected.get('sizes', category_sizes)
            # Return intersection of both
            return [s for s in product_sizes if s in category_sizes]
        
        elif parent_key == 'lower':
            category_sizes = self.child_category.get_lower_sizes()
            product_sizes = selected.get('lower_sizes', category_sizes)
            return [s for s in product_sizes if s in category_sizes]
        
        elif parent_key == 'shoes':
            category_sizes = self.child_category.get_shoe_sizes()
            product_sizes = selected.get('shoe_sizes', category_sizes)
            return [s for s in product_sizes if s in category_sizes]
        
        return []

    def get_available_upper_sizes(self):
        """Get upper sizes for combo products"""
        if not self.is_combo():
            return []
        
        category_sizes = self.child_category.get_upper_sizes()
        selected = self.selected_sizes or {}
        product_sizes = selected.get('upper_sizes', category_sizes)
        return [s for s in product_sizes if s in category_sizes]

    def get_available_lower_sizes(self):
        """Get lower sizes for combo products"""
        if not self.is_combo():
            return []
        
        category_sizes = self.child_category.get_combo_lower_sizes()
        selected = self.selected_sizes or {}
        product_sizes = selected.get('lower_sizes', category_sizes)
        return [s for s in product_sizes if s in category_sizes]

    def get_available_shoe_sizes(self):
        """Get shoe sizes for combo products"""
        if not self.is_combo():
            return []
        
        category_sizes = self.child_category.get_combo_shoe_sizes()
        selected = self.selected_sizes or {}
        product_sizes = selected.get('shoe_sizes', [])
        
        if not product_sizes:
            return []
        
        return [s for s in product_sizes if s in category_sizes]

    def has_available_shoe_sizes(self):
        """Check if this combo product has shoe sizes selected"""
        return len(self.get_available_shoe_sizes()) > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='photos/products')
    image_name = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.product_name} - {self.image_name or self.id}"



class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    # def sizes(self):
    #     return super(VariationManager, self).filter(variation_category='size', is_active=True)




variation_category_choice = (
    ('color','color'),
    # ('size','size'),
)



class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices = variation_category_choice)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        # Get variation value from first image's color
        first_img = self.images.first()
        return first_img.image_color if first_img else f"Variation {self.id}"


class VariationImage(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/variations')
    image_color = models.CharField(max_length=200, help_text="e.g., 'Front View', 'Side View' - for this color variation")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.variation} - {self.image_color}"


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
