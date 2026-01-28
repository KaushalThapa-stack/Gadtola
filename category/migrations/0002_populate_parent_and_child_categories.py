from django.db import migrations


def create_parent_categories(apps, schema_editor):
    """Create fixed parent categories"""
    ParentCategory = apps.get_model('category', 'ParentCategory')
    
    parent_categories = [
        {
            'key': 'outfit',
            'name': 'Outfit',
            'slug': 'outfit',
            'description': 'Clothing and outfit items'
        },
        {
            'key': 'shoes',
            'name': 'Shoes',
            'slug': 'shoes',
            'description': 'Footwear and shoes'
        },
        {
            'key': 'combos',
            'name': 'Combos',
            'slug': 'combos',
            'description': 'Complete outfit combinations'
        },
    ]
    
    for cat in parent_categories:
        ParentCategory.objects.get_or_create(
            key=cat['key'],
            defaults={
                'name': cat['name'],
                'slug': cat['slug'],
                'description': cat['description']
            }
        )


def create_uncategorized_child(apps, schema_editor):
    """Create safe default 'Uncategorized' child category under Outfit"""
    ParentCategory = apps.get_model('category', 'ParentCategory')
    ChildCategory = apps.get_model('category', 'ChildCategory')
    
    outfit_parent = ParentCategory.objects.get(key='outfit')
    ChildCategory.objects.get_or_create(
        name='Uncategorized',
        parent=outfit_parent,
        defaults={
            'slug': 'uncategorized',
            'description': 'Uncategorized products',
            'size_config': {'sizes': ['S', 'M', 'L', 'XL', '2XL', '3XL']}
        }
    )


def migrate_products(apps, schema_editor):
    """Migrate all existing products to Uncategorized child category"""
    ChildCategory = apps.get_model('category', 'ChildCategory')
    Product = apps.get_model('store', 'Product')
    
    uncategorized = ChildCategory.objects.get(name='Uncategorized')
    
    # Update all products to use the uncategorized child category
    Product.objects.all().update(child_category=uncategorized)


def reverse_function(apps, schema_editor):
    """Reverse operation"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
        ('store', '0008_product_child_category_product_combo_size_config_and_more'),
    ]

    operations = [
        migrations.RunPython(create_parent_categories, reverse_function),
        migrations.RunPython(create_uncategorized_child, reverse_function),
        migrations.RunPython(migrate_products, reverse_function),
    ]
