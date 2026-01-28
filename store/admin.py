from django.contrib import admin
from .models import Product, Variation, ReviewRating
from category.models import ChildCategory
from django import forms
import json


class ProductAdminForm(forms.ModelForm):
    """Custom form for product admin with dynamic size fields"""
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'combo_size_config': forms.Textarea(attrs={'rows': 4, 'cols': 60})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the child category if it exists
        instance = kwargs.get('instance')
        if instance and instance.child_category:
            cat = instance.child_category
            parent_key = cat.parent.key
            
            # Add help text based on parent category type
            if parent_key in ['outfit', 'shoes']:
                self.fields['combo_size_config'].help_text = f'Available sizes: {cat.get_sizes()}'
            elif parent_key == 'combos':
                help_text = f'''
Upper sizes: {cat.get_upper_sizes()}
Lower sizes: {cat.get_lower_sizes()}
Shoe sizes: {cat.get_shoe_sizes() if cat.has_shoe_sizes() else "Not configured"}

Enter as JSON (optional):
{{"default_upper": "S", "default_lower": "30", "default_shoe": "42"}}
                '''
                self.fields['combo_size_config'].help_text = help_text
    
    def clean(self):
        cleaned_data = super().clean()
        combo_size_config = cleaned_data.get('combo_size_config')
        child_category = cleaned_data.get('child_category')
        
        if combo_size_config and child_category:
            try:
                if isinstance(combo_size_config, str):
                    config = json.loads(combo_size_config) if combo_size_config else {}
                else:
                    config = combo_size_config
                
                parent_key = child_category.parent.key
                
                if parent_key == 'combos':
                    # Validate that default values are within allowed sizes
                    if 'default_upper' in config and config['default_upper'] not in child_category.get_upper_sizes():
                        raise forms.ValidationError('Default upper size must be from available upper sizes')
                    if 'default_lower' in config and config['default_lower'] not in child_category.get_lower_sizes():
                        raise forms.ValidationError('Default lower size must be from available lower sizes')
                    if child_category.has_shoe_sizes():
                        if 'default_shoe' in config and config['default_shoe'] not in child_category.get_shoe_sizes():
                            raise forms.ValidationError('Default shoe size must be from available shoe sizes')
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON in combo_size_config')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert string back to dict if needed
        combo_size_config = self.cleaned_data.get('combo_size_config')
        if isinstance(combo_size_config, str) and combo_size_config:
            instance.combo_size_config = json.loads(combo_size_config)
        elif not combo_size_config:
            instance.combo_size_config = {}
        if commit:
            instance.save()
        return instance


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('product_name', 'price', 'old_price', 'stock', 'child_category', 'modified_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('is_available', 'child_category__parent__name')
    search_fields = ('product_name', 'child_category__name')
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'slug', 'discription', 'child_category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'old_price', 'stock', 'is_available')
        }),
        ('Images', {
            'fields': ('image1', 'image2', 'image3', 'image4', 'image5'),
            'description': 'At least 2 images required'
        }),
        ('Features', {
            'fields': ('feature1', 'feature2', 'feature3', 'feature4', 'feature5'),
            'description': 'At least 2 features required'
        }),
        ('Size Configuration (Combos Only)', {
            'fields': ('combo_size_config',),
            'classes': ('collapse',),
            'description': 'Configure default sizes for combo products'
        }),
    )


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category','variation_value')




admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
