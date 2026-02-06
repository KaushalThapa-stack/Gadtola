from django.contrib import admin
from .models import Category, ParentCategory, ChildCategory
from django import forms
import json


class ParentCategoryAdmin(admin.ModelAdmin):
    """Read-only admin for fixed parent categories"""
    list_display = ('name', 'key', 'slug')
    readonly_fields = ('key', 'name', 'slug')
    
    def has_add_permission(self, request):
        # Prevent adding new parent categories
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting parent categories
        return False


class ChildCategoryAdminForm(forms.ModelForm):
    """Dynamic form that shows size fields based on parent category"""
    
    class Meta:
        model = ChildCategory
        fields = ['name', 'slug', 'parent', 'description', 'size_config']
        widgets = {
            'size_config': forms.Textarea(attrs={'rows': 6, 'cols': 60})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['size_config'].help_text = '''
Enter size configuration as JSON based on parent category:

Upper: {"sizes": ["S", "M", "L", "XL", "2XL", "3XL"]}

Lower: {"lower_sizes": ["28", "29", "30", "31", "32", "34", "36"]}

Shoes: {"shoe_sizes": ["39", "40", "41", "42", "43"]}

Combos (REQUIRED): {
  "upper_sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
  "lower_sizes": ["28", "29", "30", "31", "32", "34", "36"],
  "shoe_sizes": ["39", "40", "41", "42", "43"]
}
        '''
        
        # Convert dict to JSON string for display
        if self.instance and self.instance.size_config:
            self.fields['size_config'].initial = json.dumps(self.instance.size_config, indent=2)
    
    def clean(self):
        cleaned_data = super().clean()
        size_config_str = cleaned_data.get('size_config')
        
        if size_config_str:
            try:
                # Try to parse as JSON
                config = json.loads(size_config_str) if isinstance(size_config_str, str) else size_config_str
                parent = cleaned_data.get('parent')
                
                if parent:
                    parent_key = parent.key
                    
                    if parent_key == 'upper':
                        # Upper MUST have 'sizes'
                        if 'sizes' not in config:
                            raise forms.ValidationError(
                                'For Upper categories, size_config MUST contain "sizes" key'
                            )
                        # Reject other keys
                        if any(key not in ['sizes'] for key in config.keys()):
                            raise forms.ValidationError(
                                'For Upper categories, only "sizes" key is allowed'
                            )
                    
                    elif parent_key == 'lower':
                        # Lower MUST have 'lower_sizes'
                        if 'lower_sizes' not in config:
                            raise forms.ValidationError(
                                'For Lower categories, size_config MUST contain "lower_sizes" key'
                            )
                        # Reject other keys
                        if any(key not in ['lower_sizes'] for key in config.keys()):
                            raise forms.ValidationError(
                                'For Lower categories, only "lower_sizes" key is allowed'
                            )
                    
                    elif parent_key == 'shoes':
                        # Shoes MUST have 'shoe_sizes'
                        if 'shoe_sizes' not in config:
                            raise forms.ValidationError(
                                'For Shoes categories, size_config MUST contain "shoe_sizes" key'
                            )
                        # Reject other keys
                        if any(key not in ['shoe_sizes'] for key in config.keys()):
                            raise forms.ValidationError(
                                'For Shoes categories, only "shoe_sizes" key is allowed'
                            )
                    
                    elif parent_key == 'combos':
                        # Combos MUST have 'upper_sizes' and 'lower_sizes'
                        if 'upper_sizes' not in config or 'lower_sizes' not in config:
                            raise forms.ValidationError(
                                'For Combos categories, size_config MUST contain "upper_sizes" and "lower_sizes"'
                            )
                        # shoe_sizes is optional, but no other keys allowed
                        allowed_keys = {'upper_sizes', 'lower_sizes', 'shoe_sizes'}
                        if not set(config.keys()).issubset(allowed_keys):
                            raise forms.ValidationError(
                                'For Combos categories, only "upper_sizes", "lower_sizes", and optional "shoe_sizes" are allowed'
                            )
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON in size_config')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert string back to dict
        size_config_str = self.cleaned_data.get('size_config')
        if size_config_str:
            instance.size_config = json.loads(size_config_str) if isinstance(size_config_str, str) else size_config_str
        else:
            instance.size_config = {}
        if commit:
            instance.save()
        return instance


class ChildCategoryAdmin(admin.ModelAdmin):
    """Admin for child categories with dynamic size configuration"""
    form = ChildCategoryAdminForm
    list_display = ('name', 'parent', 'slug')
    list_filter = ('parent__name',)
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Size Configuration', {
            'fields': ('size_config',),
            'description': 'Configure available sizes for this category based on its parent type'
        }),
    )


admin.site.register(Category)
admin.site.register(ParentCategory, ParentCategoryAdmin)
admin.site.register(ChildCategory, ChildCategoryAdmin)
