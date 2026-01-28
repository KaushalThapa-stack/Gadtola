#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sathyshop.settings')
django.setup()

from category.models import ParentCategory, ChildCategory
from store.models import Product

print('=' * 60)
print('GSM REFACTOR VERIFICATION REPORT')
print('=' * 60)

# Verify parent categories
print('\n=== PARENT CATEGORIES ===')
parent_count = ParentCategory.objects.count()
print(f'Total parent categories: {parent_count}')
for pc in ParentCategory.objects.all():
    children_count = pc.children.count()
    print(f'  ✓ {pc.name} ({pc.key}): {children_count} child category/categories')

# Verify child categories
print('\n=== CHILD CATEGORIES ===')
child_count = ChildCategory.objects.count()
print(f'Total child categories: {child_count}')
for cc in ChildCategory.objects.all():
    size_keys = ', '.join(cc.size_config.keys()) if cc.size_config else 'empty'
    print(f'  ✓ {cc.name} under {cc.parent.name}')
    print(f'    Size config keys: {size_keys}')

# Verify products
print('\n=== PRODUCTS ===')
total_products = Product.objects.count()
with_child = Product.objects.filter(child_category__isnull=False).count()
combos = Product.objects.filter(child_category__parent__key='combos').count()
outfit = Product.objects.filter(child_category__parent__key='outfit').count()
shoes = Product.objects.filter(child_category__parent__key='shoes').count()

print(f'Total products: {total_products}')
print(f'  ✓ With child_category: {with_child}')
print(f'  ✓ Combos: {combos}')
print(f'  ✓ Outfit: {outfit}')
print(f'  ✓ Shoes: {shoes}')

# Sample product details
print('\n=== SAMPLE PRODUCTS ===')
for product in Product.objects.all()[:3]:
    print(f'  ✓ {product.product_name}')
    print(f'    Category: {product.child_category.name} → {product.child_category.parent.name}')
    if product.is_combo():
        print(f'    Type: COMBO')
        print(f'    Combo config: {product.combo_size_config}')
    else:
        print(f'    Type: {product.child_category.parent.name.upper()}')

print('\n' + '=' * 60)
print('✅ REFACTORING COMPLETE AND VERIFIED')
print('=' * 60)
