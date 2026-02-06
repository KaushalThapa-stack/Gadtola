# SIZE FILTERING FLOW DIAGRAM

## How Sizes Flow Through the System

```
┌─────────────────────────────────────────────────────────────────┐
│                      ADMIN PANEL                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Product Edit Form                                               │
│  ┌─────────────────────────────────────────────────┐             │
│  │  Product Name: Blue Shirt                       │             │
│  │  Child Category: Upper Clothing                 │             │
│  │  ...                                            │             │
│  │                                                 │             │
│  │  Size Configuration Section:                    │             │
│  │  ┌───────────────────────────────────────────┐  │             │
│  │  │ selected_sizes:                           │  │             │
│  │  │ {"sizes": ["S", "M", "L"]}               │  │             │
│  │  │                                           │  │             │
│  │  │ ✓ Validates against category allowed     │  │             │
│  │  │ ✓ Saves to database                      │  │             │
│  │  └───────────────────────────────────────────┘  │             │
│  │                                                 │             │
│  │  [SAVE]                                         │             │
│  └─────────────────────────────────────────────────┘             │
│                          │                                        │
│                          ↓                                        │
│  Form Validation         │                                       │
│  ┌─────────────────────────────────────────────────┐             │
│  │ ✓ Is "S" in category? Yes                       │             │
│  │ ✓ Is "M" in category? Yes                       │             │
│  │ ✓ Is "L" in category? Yes                       │             │
│  │ ✓ Valid JSON? Yes                               │             │
│  │                                                 │             │
│  │ → Validation PASSED → Save to DB                │             │
│  └─────────────────────────────────────────────────┘             │
│                          │                                        │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────┐
        │        DATABASE                      │
        ├──────────────────────────────────────┤
        │                                      │
        │  Product Table:                      │
        │  ┌────────────────────────────────┐  │
        │  │ id: 1                          │  │
        │  │ name: "Blue Shirt"             │  │
        │  │ selected_sizes: {              │  │
        │  │   "sizes": ["S", "M", "L"]     │  │
        │  │ }                              │  │
        │  │ child_category_id: 5           │  │
        │  └────────────────────────────────┘  │
        │                                      │
        │  ChildCategory Table:                │
        │  ┌────────────────────────────────┐  │
        │  │ id: 5                          │  │
        │  │ name: "Upper Clothing"         │  │
        │  │ parent_id: 1                   │  │
        │  │ size_config: {                 │  │
        │  │   "sizes": ["S", "M", "L",    │  │
        │  │             "XL", "2XL", "3XL"]  │
        │  │ }                              │  │
        │  └────────────────────────────────┘  │
        │                                      │
        └──────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────┐
        │  PRODUCT MODEL METHODS               │
        ├──────────────────────────────────────┤
        │                                      │
        │  product.get_available_sizes()       │
        │  ┌────────────────────────────────┐  │
        │  │ 1. Get selected_sizes:         │  │
        │  │    ["S", "M", "L"]             │  │
        │  │                                │  │
        │  │ 2. Get category allowed:       │  │
        │  │    ["S", "M", "L", "XL",      │  │
        │  │     "2XL", "3XL"]              │  │
        │  │                                │  │
        │  │ 3. Calculate intersection:     │  │
        │  │    ["S", "M", "L"]             │  │
        │  │      ∩                         │  │
        │  │    ["S", "M", "L", "XL",      │  │
        │  │     "2XL", "3XL"]              │  │
        │  │    ───────────────────         │  │
        │  │    ["S", "M", "L"]             │  │
        │  │                                │  │
        │  │ 4. Return: ["S", "M", "L"]    │  │
        │  └────────────────────────────────┘  │
        │                                      │
        └──────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────┐
        │  TEMPLATE RENDERING                  │
        ├──────────────────────────────────────┤
        │                                      │
        │  {% for size in                      │
        │      product.get_available_sizes %}  │
        │    <option>{{ size }}</option>        │
        │  {% endfor %}                        │
        │                                      │
        │  Renders:                            │
        │  <select>                            │
        │    <option>S</option>                │
        │    <option>M</option>                │
        │    <option>L</option>                │
        │  </select>                           │
        │                                      │
        │  (XL, 2XL, 3XL NOT RENDERED)        │
        │                                      │
        └──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND / BROWSER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Product Page: Blue Shirt                                        │
│  ┌─────────────────────────────────────────────┐                 │
│  │                                             │                 │
│  │  Price: $29.99                              │                 │
│  │                                             │                 │
│  │  Select Size:                               │                 │
│  │  ┌──────────────────────────────────────┐   │                 │
│  │  │ ∨ Size Dropdown                      │   │                 │
│  │  │ ┌──────────────────────────────────┐ │   │                 │
│  │  │ │ S                                │ │   │                 │
│  │  │ │ M                                │ │   │                 │
│  │  │ │ L                                │ │   │                 │
│  │  │ └──────────────────────────────────┘ │   │                 │
│  │  └──────────────────────────────────────┘   │                 │
│  │                                             │                 │
│  │  (XL, 2XL, 3XL are NOT shown)              │                 │
│  │                                             │                 │
│  │  [Add to Cart]                              │                 │
│  │                                             │                 │
│  └─────────────────────────────────────────────┘                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Size Filtering Logic (Detailed)

```
                    ┌──────────────────────┐
                    │  INTERSECTION LOGIC  │
                    └──────────────────────┘
                             │
                             ↓

        STEP 1: Get Product Selected Sizes
        ┌──────────────────────────────┐
        │ product.selected_sizes:      │
        │ {"sizes": ["S", "M", "L"]}   │
        │                              │
        │ OR if empty/not set:         │
        │ Use all category sizes       │
        └──────────────────────────────┘
                    ∩
        STEP 2: Get Category Allowed Sizes
        ┌──────────────────────────────┐
        │ category.size_config:        │
        │ {                            │
        │   "sizes": [                 │
        │     "S", "M", "L",           │
        │     "XL", "2XL", "3XL"       │
        │   ]                          │
        │ }                            │
        └──────────────────────────────┘
                    ∩
        STEP 3: Calculate Intersection
        ┌──────────────────────────────┐
        │ Product ∩ Category =         │
        │                              │
        │ ["S", "M", "L"]              │
        │        ∩                     │
        │ ["S", "M", "L", "XL",        │
        │  "2XL", "3XL"]               │
        │        =                     │
        │ ["S", "M", "L"]              │
        │                              │
        │ (Only sizes in BOTH lists)   │
        └──────────────────────────────┘
                    │
                    ↓
        STEP 4: Display Result
        ┌──────────────────────────────┐
        │ Frontend Shows:              │
        │ ✓ S                          │
        │ ✓ M                          │
        │ ✓ L                          │
        │ ✗ XL (not selected)          │
        │ ✗ 2XL (not selected)         │
        │ ✗ 3XL (not selected)         │
        └──────────────────────────────┘
```

---

## Combo Product Flow (Special Case)

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMBO PRODUCT FLOW                            │
└─────────────────────────────────────────────────────────────────┘

        Product: "Full Outfit - Shirt + Pants"
        
        selected_sizes:
        {
          "upper_sizes": ["S", "M"],
          "lower_sizes": ["28", "30"],
          "shoe_sizes": ["39"]
        }

        ChildCategory (Combos) size_config:
        {
          "upper_sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
          "lower_sizes": ["28", "29", "30", "31", "32", "34", "36"],
          "shoe_sizes": ["39", "40", "41", "42", "43"]
        }


                            ↓


        TEMPLATE:

        Upper Selector:
        {% for size in product.get_available_upper_sizes %}
          <option>{{ size }}</option>
        {% endfor %}
        
        Shows: S, M (intersection of ["S", "M"] and category)


        Lower Selector:
        {% for size in product.get_available_lower_sizes %}
          <option>{{ size }}</option>
        {% endfor %}
        
        Shows: 28, 30 (intersection of ["28", "30"] and category)


        Shoe Selector Visibility:
        {% if product.has_available_shoe_sizes %}
          <select>
            {% for size in product.get_available_shoe_sizes %}
              <option>{{ size }}</option>
            {% endfor %}
          </select>
        {% endif %}
        
        SHOWN: shoe_sizes is ["39"], so ✓ VISIBLE
        Shows: 39


                            ↓


        FRONTEND RENDERS:

        Upper Size Dropdown:
        ┌─────────────┐
        │ S           │
        │ M           │
        └─────────────┘

        Lower Size Dropdown:
        ┌─────────────┐
        │ 28          │
        │ 30          │
        └─────────────┘

        Shoe Size Dropdown: ✓ VISIBLE
        ┌─────────────┐
        │ 39          │
        └─────────────┘


IF shoe_sizes was empty or not set:

        selected_sizes:
        {
          "upper_sizes": ["S", "M"],
          "lower_sizes": ["28", "30"]
          ← No shoe_sizes key
        }

        SHOE SELECTOR: ✗ HIDDEN (not rendered at all)
```

---

## Admin vs. Frontend Sync

```
SCENARIO: Admin removes size "M"

┌─────────────────────┐
│ ADMIN PANEL         │
├─────────────────────┤
│ Current:            │
│ {"sizes":           │
│   ["S", "M", "L"]   │
│ }                   │
│                     │
│ Admin edits to:     │
│ {"sizes":           │
│   ["S", "L"]        │
│ }                   │
│                     │
│ Clicks: SAVE        │
└─────────────────────┘
         │
         │ Validation
         │ "S" in category? ✓
         │ "L" in category? ✓
         ↓
┌─────────────────────┐
│ DATABASE            │
├─────────────────────┤
│ UPDATE Product      │
│ selected_sizes:     │
│ {"sizes":           │
│   ["S", "L"]        │
│ }                   │
│                     │
│ WHERE id = 1        │
│                     │
│ ✓ UPDATE COMPLETE   │
└─────────────────────┘
         │
         ↓
    (Wait a moment)
         │
         ↓
┌─────────────────────┐
│ CUSTOMER REFRESH    │
├─────────────────────┤
│ Clicks refresh in   │
│ browser             │
│                     │
│ Page reloads        │
│ Product fetched     │
│ from database       │
│                     │
│ get_available_sizes()
│ calculates:         │
│ ["S", "L"] ∩       │
│ category            │
│                     │
│ = ["S", "L"]        │
│                     │
│ Template renders    │
│ only S and L        │
│                     │
│ ✓ "M" GONE!         │
└─────────────────────┘

NO CACHE CLEARING NEEDED!
INSTANT SYNC!
```

---

## Default Behavior (Backward Compatibility)

```
SCENARIO: Admin doesn't set selected_sizes

Product 1: No selected_sizes set
┌─────────────────────────────────────┐
│ selected_sizes: {} (empty)          │
│                                     │
│ get_available_sizes() logic:        │
│                                     │
│ product_sizes = selected.get(       │
│   'sizes',                          │
│   category.get_sizes()  ← FALLBACK  │
│ )                                   │
│                                     │
│ Returns all category sizes:         │
│ ["S", "M", "L", "XL", "2XL", "3XL"]│
│                                     │
│ ✓ Works like before                 │
│ ✓ Backward compatible               │
└─────────────────────────────────────┘
```

---

## Error Cases

```
CASE 1: Invalid Size in Admin
┌──────────────────────────────┐
│ Admin enters:                │
│ {"sizes": ["S", "XYZ"]}      │
│                              │
│ Validation checks:           │
│ "S" in category? ✓           │
│ "XYZ" in category? ✗ ERROR!  │
│                              │
│ Form shows error message:    │
│ "Size 'XYZ' not available"   │
│                              │
│ Data NOT saved               │
│ Original data kept           │
└──────────────────────────────┘


CASE 2: Invalid JSON
┌──────────────────────────────┐
│ Admin enters:                │
│ {"sizes": ['S', 'M']}        │
│         ↑ Wrong quotes       │
│                              │
│ JSON validator fails         │
│                              │
│ Form shows error message:    │
│ "Invalid JSON in selected_*" │
│                              │
│ Data NOT saved               │
│ Original data kept           │
└──────────────────────────────┘
```

---

## Summary

```
SIMPLE FORMULA:

Frontend Shown = (Product Selected) ∩ (Category Allowed)

WHERE:
  ∩ = Intersection (only sizes in BOTH)

EXAMPLE:
  Product Selected: ["S", "M"]
  Category Allowed: ["S", "M", "L", "XL"]
  ───────────────────────────────────────
  Frontend Shows: ["S", "M"]

ANOTHER EXAMPLE:
  Product Selected: (not set, use all)
  Category Allowed: ["S", "M", "L", "XL"]
  ───────────────────────────────────────
  Frontend Shows: ["S", "M", "L", "XL"]

COMBO EXAMPLE:
  Product Upper: ["S", "M"]
  Product Lower: ["28", "30"]
  Product Shoe: [] (empty)
  Category: (has all sizes)
  ───────────────────────────────────────
  Frontend Upper: ["S", "M"]
  Frontend Lower: ["28", "30"]
  Frontend Shoe: HIDDEN (no sizes)
```

This is the core logic that fixes all three bugs.
