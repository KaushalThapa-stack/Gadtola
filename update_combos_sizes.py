#!/usr/bin/env python
"""
Update existing Combos child categories to have full size list
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sathyshop.settings')
django.setup()

from category.models import ChildCategory

FULL_COMBO_SIZES = {
    "upper_sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
    "lower_sizes": ["28", "29", "30", "31", "32", "34", "36"],
    "shoe_sizes": ["39", "40", "41", "42", "43"]
}

def update_combos():
    combos = ChildCategory.objects.filter(parent__key='combos')
    
    print(f"Found {combos.count()} combo child categories")
    
    for combo in combos:
        old_config = combo.size_config.copy() if combo.size_config else {}
        
        # Update with full sizes while preserving any existing structure
        new_config = {
            "upper_sizes": FULL_COMBO_SIZES["upper_sizes"],
            "lower_sizes": FULL_COMBO_SIZES["lower_sizes"],
            "shoe_sizes": old_config.get("shoe_sizes", FULL_COMBO_SIZES["shoe_sizes"])
        }
        
        combo.size_config = new_config
        combo.save()
        
        print(f"✓ Updated: {combo.name}")
        print(f"  Upper: {new_config['upper_sizes']}")
        print(f"  Lower: {new_config['lower_sizes']}")
        print(f"  Shoe: {new_config['shoe_sizes']}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("UPDATING COMBO CHILD CATEGORIES WITH FULL SIZE LIST")
    print("="*60 + "\n")
    
    update_combos()
    
    print("\n" + "="*60)
    print("UPDATE COMPLETE")
    print("="*60)
