#!/usr/bin/env python
"""
Test script to verify all size-related fixes
- BUG 1: Product size removal now reflects on frontend
- BUG 2: Combos child category has full size list
- BUG 3: Combo products show only selected sizes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sathyshop.settings')
django.setup()

from category.models import ParentCategory, ChildCategory
from store.models import Product
import json

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def test_combos_size_config():
    """Test BUG 2: Combos have full size list"""
    print_section("BUG 2: Testing Combos Child Category Full Size List")
    
    try:
        combos_parent = ParentCategory.objects.get(key='combos')
        print(f"✓ Found Combos parent category")
        
        combo_children = combos_parent.children.all()
        if not combo_children.exists():
            print("⚠ No Combo child categories exist. Creating one for testing...")
            combo_child = ChildCategory.objects.create(
                name='Test Combo',
                slug='test-combo',
                parent=combos_parent,
                size_config={
                    "upper_sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
                    "lower_sizes": ["28", "29", "30", "31", "32", "34", "36"],
                    "shoe_sizes": ["39", "40", "41", "42", "43"]
                }
            )
            combo_children = [combo_child]
            print(f"✓ Created test combo child category")
        
        for child in combo_children:
            config = child.size_config
            print(f"\nCombo Child: {child.name}")
            print(f"  Upper sizes: {config.get('upper_sizes', [])}")
            print(f"  Lower sizes: {config.get('lower_sizes', [])}")
            print(f"  Shoe sizes: {config.get('shoe_sizes', [])}")
            
            # Verify full list
            expected_upper = ["S", "M", "L", "XL", "2XL", "3XL"]
            expected_lower = ["28", "29", "30", "31", "32", "34", "36"]
            expected_shoe = ["39", "40", "41", "42", "43"]
            
            upper_match = set(config.get('upper_sizes', [])) >= set(expected_upper)
            lower_match = set(config.get('lower_sizes', [])) >= set(expected_lower)
            shoe_match = set(config.get('shoe_sizes', [])) >= set(expected_shoe)
            
            if upper_match and lower_match and shoe_match:
                print(f"✓ {child.name} has full size list")
            else:
                print(f"✗ {child.name} is missing sizes")
                if not upper_match:
                    print(f"  Missing upper: {set(expected_upper) - set(config.get('upper_sizes', []))}")
                if not lower_match:
                    print(f"  Missing lower: {set(expected_lower) - set(config.get('lower_sizes', []))}")
                if not shoe_match:
                    print(f"  Missing shoe: {set(expected_shoe) - set(config.get('shoe_sizes', []))}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_product_selected_sizes():
    """Test BUG 1: Product size removal now persists"""
    print_section("BUG 1: Testing Product Selected Sizes Field")
    
    try:
        # Check if any product exists
        products = Product.objects.filter(is_available=True)[:3]
        
        if not products.exists():
            print("⚠ No products found for testing")
            return
        
        for product in products:
            print(f"\nProduct: {product.product_name}")
            print(f"  Child Category: {product.child_category}")
            print(f"  Parent Category: {product.child_category.parent.name if product.child_category else 'N/A'}")
            
            # Check selected_sizes field
            if product.selected_sizes:
                print(f"  Selected Sizes (JSON): {json.dumps(product.selected_sizes, indent=4)}")
                print(f"  ✓ Product has selected_sizes configured")
            else:
                print(f"  Selected Sizes: (empty - will use all category sizes)")
                print(f"  ⚠ Hint: Admin can set specific sizes for this product")
            
            # Test the new methods
            if product.child_category:
                parent_key = product.child_category.parent.key
                
                if parent_key == 'upper':
                    available = product.get_available_sizes()
                    print(f"  Available Upper Sizes: {available}")
                    
                elif parent_key == 'lower':
                    available = product.get_available_sizes()
                    print(f"  Available Lower Sizes: {available}")
                    
                elif parent_key == 'shoes':
                    available = product.get_available_sizes()
                    print(f"  Available Shoe Sizes: {available}")
                    
                elif parent_key == 'combos':
                    upper = product.get_available_upper_sizes()
                    lower = product.get_available_lower_sizes()
                    shoe = product.get_available_shoe_sizes()
                    has_shoe = product.has_available_shoe_sizes()
                    
                    print(f"  Available Upper Sizes: {upper}")
                    print(f"  Available Lower Sizes: {lower}")
                    print(f"  Available Shoe Sizes: {shoe if shoe else '(none selected)'}")
                    print(f"  Has Shoe Sizes: {has_shoe}")
                    
                    if not has_shoe:
                        print(f"  ✓ Shoe selector will be hidden on frontend")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_size_intersection_logic():
    """Test BUG 3: Frontend shows intersection of product and category sizes"""
    print_section("BUG 3: Testing Size Intersection Logic")
    
    try:
        # Find a combo product
        combos = Product.objects.filter(
            child_category__parent__key='combos',
            is_available=True
        )
        
        if not combos.exists():
            print("⚠ No combo products found for testing")
            print("  Hint: Create a combo product and assign sizes in admin")
            return
        
        product = combos[0]  # Get first result without slicing
        print(f"\nCombo Product: {product.product_name}")
        print(f"Child Category: {product.child_category.name}")
        
        # Category sizes
        cat = product.child_category
        cat_upper = set(cat.get_upper_sizes())
        cat_lower = set(cat.get_combo_lower_sizes())
        cat_shoe = set(cat.get_combo_shoe_sizes())
        
        print(f"\nCategory Allowed Sizes:")
        print(f"  Upper: {sorted(cat_upper)}")
        print(f"  Lower: {sorted(cat_lower)}")
        print(f"  Shoe: {sorted(cat_shoe)}")
        
        # Product selected sizes
        selected = product.selected_sizes or {}
        prod_upper = set(selected.get('upper_sizes', []))
        prod_lower = set(selected.get('lower_sizes', []))
        prod_shoe = set(selected.get('shoe_sizes', []))
        
        print(f"\nProduct Selected Sizes:")
        print(f"  Upper: {sorted(prod_upper) if prod_upper else '(use all category)'}")
        print(f"  Lower: {sorted(prod_lower) if prod_lower else '(use all category)'}")
        print(f"  Shoe: {sorted(prod_shoe) if prod_shoe else '(none)'}")
        
        # Frontend will show
        front_upper = product.get_available_upper_sizes()
        front_lower = product.get_available_lower_sizes()
        front_shoe = product.get_available_shoe_sizes()
        
        print(f"\nFrontend Will Show (Intersection):")
        print(f"  Upper: {sorted(front_upper)}")
        print(f"  Lower: {sorted(front_lower)}")
        print(f"  Shoe: {sorted(front_shoe) if front_shoe else '(hidden)'}")
        
        # Verify intersection logic
        if prod_upper:
            expected_upper = prod_upper & cat_upper
            if set(front_upper) == expected_upper:
                print(f"✓ Upper size intersection correct")
            else:
                print(f"✗ Upper size intersection FAILED")
        
        if prod_lower:
            expected_lower = prod_lower & cat_lower
            if set(front_lower) == expected_lower:
                print(f"✓ Lower size intersection correct")
            else:
                print(f"✗ Lower size intersection FAILED")
        
        if prod_shoe:
            expected_shoe = prod_shoe & cat_shoe
            if set(front_shoe) == expected_shoe:
                print(f"✓ Shoe size intersection correct")
            else:
                print(f"✗ Shoe size intersection FAILED")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def test_admin_validation():
    """Test admin form validation"""
    print_section("Testing Admin Form Validation")
    
    try:
        from store.admin import ProductAdminForm
        from category.models import ChildCategory
        
        # Get a child category for testing
        child = ChildCategory.objects.first()
        if not child:
            print("⚠ No child categories exist")
            return
        
        print(f"Testing ProductAdminForm validation with child category: {child.name}")
        print(f"Parent: {child.parent.name}")
        
        # Test form with invalid size
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        
        data = {
            'product_name': 'Test Product',
            'slug': 'test-product',
            'price': 100,
            'stock': 10,
            'is_available': True,
            'child_category': child.id,
            'selected_sizes': '{"sizes": ["XYZ"]}',  # Invalid size
        }
        
        form = ProductAdminForm(data)
        if not form.is_valid():
            print(f"✓ Form correctly rejects invalid size 'XYZ'")
            print(f"  Error: {form.errors.get('selected_sizes', ['Unknown error'])[0] if 'selected_sizes' in form.errors else form.errors}")
        else:
            print(f"⚠ Form accepted invalid size (expected validation to fail)")
        
        # Test with valid size
        if child.parent.key == 'upper':
            valid_size = child.get_sizes()[0] if child.get_sizes() else 'S'
            data['selected_sizes'] = json.dumps({'sizes': [valid_size]})
        
        form2 = ProductAdminForm(data)
        if form2.is_valid():
            print(f"✓ Form accepts valid sizes")
        else:
            print(f"⚠ Form rejected valid sizes: {form2.errors}")
        
    except Exception as e:
        print(f"⚠ Cannot test admin form: {e}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SIZE FIX VERIFICATION TEST SUITE")
    print("="*60)
    
    test_combos_size_config()
    test_product_selected_sizes()
    test_size_intersection_logic()
    test_admin_validation()
    
    print_section("TEST SUITE COMPLETE")
    print("\nNext Steps:")
    print("1. Go to Django Admin")
    print("2. Edit/create a product in an Upper/Lower/Shoes category")
    print("3. In 'Size Configuration' section, enter selected_sizes as JSON")
    print("4. For example: {\"sizes\": [\"S\", \"M\", \"L\"]}")
    print("5. Save and view product detail on frontend")
    print("6. Only selected sizes should appear in dropdown")
    print("\nFor Combos:")
    print("1. Make sure Combo child category has full size list configured")
    print("2. Create/edit a combo product")
    print("3. Set selected upper/lower/shoe sizes")
    print("4. Shoe size selector will hide if no shoe sizes selected")
