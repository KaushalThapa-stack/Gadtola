from django.db import models
from category.models import Category, ChildCategory
from django.urls import reverse
from accounts.models import Account
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count


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
    
    # Size data for combos (stores selected size combinations)
    # Format: {'default_upper': 'S', 'default_lower': '30', 'default_shoe': '42'}
    combo_size_config = models.JSONField(default=dict, blank=True)
    
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

    def is_outfit(self):
        """Check if product is from Outfit parent category"""
        if self.child_category:
            return self.child_category.parent.key == 'outfit'
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
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


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
