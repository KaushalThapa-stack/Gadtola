from django.contrib import admin
from .models import Product, Variation, ReviewRating, Brand, ProductImage, VariationImage
from category.models import ChildCategory
from django import forms
import json
from django.forms.models import BaseInlineFormSet


# ============ Inline FormSets and Inlines (must be before ProductAdmin) ============

class ProductImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('image'):
                    images += 1

        if images < 4:
            raise forms.ValidationError('Please provide at least 4 product images.')
        if images > 5:
            raise forms.ValidationError('You can provide a maximum of 5 product images.')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 5
    formset = ProductImageInlineFormSet
    fields = ('image', 'image_name', 'order')


class VariationImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('image'):
                    images += 1

        if images < 1:
            raise forms.ValidationError('Each variation requires at least 1 image (with a color name).')
        if images > 20:
            raise forms.ValidationError('A variation can have a maximum of 20 images.')


class VariationImageInline(admin.TabularInline):
    model = VariationImage
    extra = 1
    max_num = 20
    formset = VariationImageInlineFormSet
    fields = ('image', 'image_color', 'order')


# ============ Form Classes ============

class ProductAdminForm(forms.ModelForm):
    """Custom form for product admin with dynamic size fields"""
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'combo_size_config': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
            'selected_sizes': forms.Textarea(attrs={'rows': 4, 'cols': 60})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the child category if it exists
        instance = kwargs.get('instance')
        if instance and instance.child_category:
            cat = instance.child_category
            parent_key = cat.parent.key
            
            # Add help text based on parent category type
            if parent_key == 'upper':
                available_sizes = cat.get_sizes()
                self.fields['selected_sizes'].help_text = f'Upper sizes from category: {available_sizes}. Enter as JSON: {{"sizes": ["S", "M", "L"]}}'
            elif parent_key == 'lower':
                available_sizes = cat.get_lower_sizes()
                self.fields['selected_sizes'].help_text = f'Lower sizes from category: {available_sizes}. Enter as JSON: {{"lower_sizes": ["28", "30", "32"]}}'
            elif parent_key == 'shoes':
                available_sizes = cat.get_shoe_sizes()
                self.fields['selected_sizes'].help_text = f'Shoe sizes from category: {available_sizes}. Enter as JSON: {{"shoe_sizes": ["39", "40", "41"]}}'
            elif parent_key == 'combos':
                upper_sizes = cat.get_upper_sizes()
                lower_sizes = cat.get_combo_lower_sizes()
                shoe_sizes = cat.get_combo_shoe_sizes() if cat.has_shoe_sizes() else []
                help_text = f'''Combo sizes to assign to this product. Available:
Upper: {upper_sizes}
Lower: {lower_sizes}
Shoe: {shoe_sizes if shoe_sizes else "Not configured"}

Enter as JSON:
{{"upper_sizes": ["S", "M"], "lower_sizes": ["28", "30"]}}
'''
                self.fields['selected_sizes'].help_text = help_text
            
            # Convert instance data for display
            if instance and instance.selected_sizes:
                self.fields['selected_sizes'].initial = json.dumps(instance.selected_sizes, indent=2)
    
    def clean(self):
        cleaned_data = super().clean()
        selected_sizes_str = cleaned_data.get('selected_sizes')
        combo_size_config = cleaned_data.get('combo_size_config')
        child_category = cleaned_data.get('child_category')
        
        # Validate selected_sizes
        if selected_sizes_str and child_category:
            try:
                if isinstance(selected_sizes_str, str):
                    selected_sizes = json.loads(selected_sizes_str) if selected_sizes_str else {}
                else:
                    selected_sizes = selected_sizes_str
                
                parent_key = child_category.parent.key
                
                if parent_key == 'upper':
                    allowed_sizes = child_category.get_sizes()
                    if 'sizes' in selected_sizes:
                        for size in selected_sizes['sizes']:
                            if size not in allowed_sizes:
                                raise forms.ValidationError(f'Size "{size}" is not available in this category')
                
                elif parent_key == 'lower':
                    allowed_sizes = child_category.get_lower_sizes()
                    if 'lower_sizes' in selected_sizes:
                        for size in selected_sizes['lower_sizes']:
                            if size not in allowed_sizes:
                                raise forms.ValidationError(f'Size "{size}" is not available in this category')
                
                elif parent_key == 'shoes':
                    allowed_sizes = child_category.get_shoe_sizes()
                    if 'shoe_sizes' in selected_sizes:
                        for size in selected_sizes['shoe_sizes']:
                            if size not in allowed_sizes:
                                raise forms.ValidationError(f'Size "{size}" is not available in this category')
                
                elif parent_key == 'combos':
                    upper_allowed = child_category.get_upper_sizes()
                    lower_allowed = child_category.get_combo_lower_sizes()
                    shoe_allowed = child_category.get_combo_shoe_sizes() if child_category.has_shoe_sizes() else []
                    
                    if 'upper_sizes' in selected_sizes:
                        for size in selected_sizes['upper_sizes']:
                            if size not in upper_allowed:
                                raise forms.ValidationError(f'Upper size "{size}" is not available in this category')
                    
                    if 'lower_sizes' in selected_sizes:
                        for size in selected_sizes['lower_sizes']:
                            if size not in lower_allowed:
                                raise forms.ValidationError(f'Lower size "{size}" is not available in this category')
                    
                    if 'shoe_sizes' in selected_sizes and shoe_allowed:
                        for size in selected_sizes['shoe_sizes']:
                            if size not in shoe_allowed:
                                raise forms.ValidationError(f'Shoe size "{size}" is not available in this category')
            
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON in selected_sizes')
        
        # Validate combo_size_config
        if combo_size_config and child_category:
            try:
                if isinstance(combo_size_config, str):
                    config = json.loads(combo_size_config) if combo_size_config else {}
                else:
                    config = combo_size_config
                
                parent_key = child_category.parent.key
                
                if parent_key == 'upper':
                    # Upper products have no default size config required
                    pass
                elif parent_key == 'lower':
                    # Lower products have no default size config required
                    pass
                elif parent_key == 'shoes':
                    # Shoes products have no default size config required
                    pass
                elif parent_key == 'combos':
                    # Validate that default values are within allowed sizes
                    if 'default_upper' in config and config['default_upper'] not in child_category.get_upper_sizes():
                        raise forms.ValidationError('Default upper size must be from available upper sizes')
                    if 'default_lower' in config and config['default_lower'] not in child_category.get_combo_lower_sizes():
                        raise forms.ValidationError('Default lower size must be from available lower sizes')
                    if child_category.has_shoe_sizes():
                        if 'default_shoe' in config and config['default_shoe'] not in child_category.get_combo_shoe_sizes():
                            raise forms.ValidationError('Default shoe size must be from available shoe sizes')
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON in combo_size_config')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert selected_sizes string back to dict if needed
        selected_sizes = self.cleaned_data.get('selected_sizes')
        if isinstance(selected_sizes, str) and selected_sizes:
            instance.selected_sizes = json.loads(selected_sizes)
        elif not selected_sizes:
            instance.selected_sizes = {}
        
        # Convert combo_size_config string back to dict if needed
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
    inlines = (ProductImageInline,)
    list_display = ('product_name', 'price', 'old_price', 'stock', 'child_category', 'brand', 'modified_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('is_available', 'child_category__parent__name', 'brand')
    search_fields = ('product_name', 'child_category__name', 'brand__name')
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'slug', 'discription', 'child_category', 'brand')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'old_price', 'stock', 'is_available')
        }),
        ('Images', {
            'fields': (),
            'description': 'Upload exactly 4 product images (1 additional optional) using the Product Images inline below.'
        }),
        ('Features', {
            'fields': ('feature1', 'feature2', 'feature3', 'feature4', 'feature5'),
            'description': 'At least 2 features required'
        }),
        ('Size Configuration', {
            'fields': ('selected_sizes', 'combo_size_config'),
            'description': 'For regular products: select specific sizes. For combos: optionally set default sizes.'
        }),
    )




class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','get_color_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category')
    inlines = (VariationImageInline,)
    
    def get_color_value(self, obj):
        first_img = obj.images.first()
        return first_img.image_color if first_img else '-'
    get_color_value.short_description = 'Color'


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    
    def logo_preview(self, obj):
        if obj.logo:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = "Logo"


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductImage)
admin.site.register(VariationImage)
