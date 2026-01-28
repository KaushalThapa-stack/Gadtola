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
Enter size configuration as JSON.
- For Outfit/Shoes: {"sizes": ["S", "M", "L", "XL", "2XL", "3XL"]}
- For Combos: {"upper_sizes": ["S", "M", "L", "XL"], "lower_sizes": ["28", "30", "32", "34"], "shoe_sizes": ["39", "40", "41", "42"]}
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
                    if parent.key in ['outfit', 'shoes']:
                        # Check that 'sizes' key exists
                        if 'sizes' not in config:
                            raise forms.ValidationError(
                                'For Outfit/Shoes categories, size_config must have "sizes" key'
                            )
                    elif parent.key == 'combos':
                        # Check that at least upper_sizes and lower_sizes exist
                        if 'upper_sizes' not in config or 'lower_sizes' not in config:
                            raise forms.ValidationError(
                                'For Combos categories, size_config must have "upper_sizes" and "lower_sizes"'
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
