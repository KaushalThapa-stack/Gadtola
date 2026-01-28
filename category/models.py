from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField
import json

# Legacy Category model - kept for backward compatibility
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description= models.TextField(max_length=150, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
            return reverse('products_by_category', args= [self.slug])

    def __str__(self):
        return self.category_name


# Fixed parent categories - system-defined
PARENT_CATEGORY_CHOICES = (
    ('outfit', 'Outfit'),
    ('shoes', 'Shoes'),
    ('combos', 'Combos'),
)


class ParentCategory(models.Model):
    """Fixed system-defined parent categories"""
    key = models.CharField(max_length=50, unique=True, choices=PARENT_CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'parent category'
        verbose_name_plural = 'parent categories'

    def __str__(self):
        return self.name


class ChildCategory(models.Model):
    """Child categories under parent categories with size configuration"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    parent = models.ForeignKey(ParentCategory, on_delete=models.CASCADE, related_name='children')
    description = models.TextField(blank=True)
    
    # Size configuration - stored as JSON for flexibility
    # For OUTFIT and SHOES: single list of sizes
    # For COMBOS: upper_sizes, lower_sizes, shoe_sizes (optional)
    size_config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'child category'
        verbose_name_plural = 'child categories'
        unique_together = ('name', 'parent')

    def __str__(self):
        return f"{self.name} ({self.parent.name})"

    def get_sizes(self):
        """Get sizes based on parent category type"""
        if self.parent.key in ['outfit', 'shoes']:
            return self.size_config.get('sizes', [])
        return []

    def get_upper_sizes(self):
        """For combos: get upper sizes"""
        if self.parent.key == 'combos':
            return self.size_config.get('upper_sizes', [])
        return []

    def get_lower_sizes(self):
        """For combos: get lower sizes"""
        if self.parent.key == 'combos':
            return self.size_config.get('lower_sizes', [])
        return []

    def get_shoe_sizes(self):
        """For combos: get shoe sizes (optional)"""
        if self.parent.key == 'combos':
            return self.size_config.get('shoe_sizes', [])
        return []

    def has_shoe_sizes(self):
        """Check if shoe sizes are defined for combos"""
        return bool(self.get_shoe_sizes())