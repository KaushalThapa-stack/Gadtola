# QUICK START GUIDE - SIZE CONFIGURATION

## For Admin Users

---

## 5-Minute Setup

### Step 1: Go to Product Admin
1. Login to Django Admin
2. Click: **Store > Products**

### Step 2: Edit/Create a Product

Choose one:
- **Edit Existing**: Click product name
- **Add New**: Click "Add Product" button

### Step 3: Scroll to "Size Configuration"

You'll see two fields:
- `combo_size_config` - For default sizes (Combos only)
- `selected_sizes` - For which sizes this product has

### Step 4: Set Selected Sizes

Copy-paste the JSON for your category:

#### Upper Category
```json
{"sizes": ["S", "M", "L", "XL"]}
```

#### Lower Category
```json
{"lower_sizes": ["28", "30", "32", "34"]}
```

#### Shoes Category
```json
{"shoe_sizes": ["39", "40", "41"]}
```

#### Combo Category
```json
{"upper_sizes": ["S", "M"], "lower_sizes": ["28", "30"]}
```

**Optional for Combos** (shows shoe selector):
```json
{
  "upper_sizes": ["S", "M"],
  "lower_sizes": ["28", "30"],
  "shoe_sizes": ["39", "40"]
}
```

### Step 5: Click "Save"

Done! Go to the product page to see the changes.

---

## Examples

### Example 1: Upper T-Shirt (Small Sizes Only)
```json
{"sizes": ["S", "M"]}
```
- Frontend shows: S, M
- L, XL, 2XL, 3XL hidden

### Example 2: Lower Jeans (Standard Sizes)
```json
{"lower_sizes": ["28", "30", "32", "34", "36"]}
```
- Frontend shows: 28, 30, 32, 34, 36
- Other sizes hidden

### Example 3: Shoes (Limited Stock)
```json
{"shoe_sizes": ["40", "41", "42"]}
```
- Frontend shows: 40, 41, 42
- 39, 43 hidden

### Example 4: Combo (Shirt + Pants)
```json
{
  "upper_sizes": ["M", "L", "XL"],
  "lower_sizes": ["30", "32", "34"]
}
```
- Upper dropdown: M, L, XL
- Lower dropdown: 30, 32, 34
- Shoe dropdown: **HIDDEN** (no shoe_sizes)

### Example 5: Combo (Full Set with Shoes)
```json
{
  "upper_sizes": ["S", "M"],
  "lower_sizes": ["28", "30"],
  "shoe_sizes": ["39", "40", "41"]
}
```
- Upper dropdown: S, M
- Lower dropdown: 28, 30
- Shoe dropdown: 39, 40, 41 **VISIBLE** (has shoe_sizes)

---

## Common Tasks

### Remove a Size from Product
**Before**:
```json
{"sizes": ["S", "M", "L", "XL"]}
```

**After** (removed L):
```json
{"sizes": ["S", "M", "XL"]}
```

Save → L disappears from frontend instantly

---

### Add More Sizes
**Before**:
```json
{"lower_sizes": ["28", "30"]}
```

**After** (added more):
```json
{"lower_sizes": ["28", "29", "30", "31", "32"]}
```

Save → New sizes appear on frontend

---

### Copy Sizes from Another Product
1. Open product A (has sizes you want)
2. Copy the `selected_sizes` value
3. Open product B
4. Paste into `selected_sizes`
5. Save

Now both have the same sizes!

---

### Make a Product "Out of Stock" (All Sizes)
Leave `selected_sizes` empty:
```json
{}
```

Frontend will show empty dropdown (no sizes available).

---

### Show All Available Sizes
Leave `selected_sizes` completely empty or just:
```json
{}
```

Product will use all sizes from the child category.

---

## Troubleshooting

### Sizes Not Showing on Frontend
**Check**:
1. ✓ `selected_sizes` is valid JSON (use JSON validator)
2. ✓ Sizes exist in child category
3. ✓ Product has correct child category set
4. ✓ Clear browser cache

**Example**:
- Category has: S, M, L, XL
- You set: `{"sizes": ["S", "M", "XYZ"]}`
- XYZ doesn't exist → ERROR
- Use: `{"sizes": ["S", "M"]}` instead

---

### Shoe Selector Not Showing
**For Combos**:
- Shoe selector appears only if `shoe_sizes` is set
- Make sure to include it in JSON:
```json
{
  "upper_sizes": [...],
  "lower_sizes": [...],
  "shoe_sizes": ["39", "40"]  ← This makes it show
}
```

If you don't want shoes, leave it out:
```json
{
  "upper_sizes": [...],
  "lower_sizes": [...]
  ← No shoe_sizes = no selector
}
```

---

### JSON Validation Error
**Error**: "Invalid JSON in selected_sizes"

**Solution**: 
- Use a JSON validator: https://jsonlint.com/
- Check for:
  - Missing commas
  - Extra commas
  - Unclosed brackets
  - Single quotes (use double quotes instead)

**Bad**:
```json
{"sizes": ['S', 'M']}  ← Wrong quotes
{"sizes": ["S" "M"]}   ← Missing comma
```

**Good**:
```json
{"sizes": ["S", "M"]}
```

---

### Size Not in Category
**Error**: "Size XL not available in this category"

**Solution**:
- Check child category configuration
- Go to: **Category > Child Categories**
- Click the child category
- Check `size_config` includes your size

Example for Upper category size_config:
```json
{
  "sizes": ["S", "M", "L", "XL", "2XL", "3XL"]
}
```

If "2XL" is missing, add it there first.

---

## Advanced Usage

### Multiple Categories, Same Sizes
If several products share the same sizes:

1. Create a template document
2. Copy-paste for each product

**Template for Standard Sizes**:
```json
{"sizes": ["S", "M", "L", "XL"]}
```

Use for all products needing these sizes.

---

### Seasonal Size Updates
**Summer Collection** (fewer large sizes):
```json
{"sizes": ["XS", "S", "M", "L"]}
```

**Winter Collection** (more large sizes):
```json
{"sizes": ["M", "L", "XL", "2XL", "3XL"]}
```

---

### Sale: Limited Sizes Only
**Normal Product**:
```json
{"sizes": ["S", "M", "L", "XL"]}
```

**Sale Product** (few left):
```json
{"sizes": ["L", "XL"]}
```

---

## Key Points

✓ **Intersection Logic**: Frontend shows only sizes in BOTH:
  - Child category allowed list
  - Product selected list

✓ **Instant Updates**: No cache clearing needed. Changes appear immediately.

✓ **Backward Compatible**: Products without `selected_sizes` use all category sizes.

✓ **No Code Changes**: All managed through admin panel.

✓ **Flexible**: Change anytime without technical help.

---

## Where to Get Help

1. **In Admin**: Hover over field → help text shows examples
2. **Docs**: See SIZE_FIXES_DOCUMENTATION.md in project root
3. **JSON Format**: Use https://jsonlint.com/ to validate
4. **JSON Examples**: This document has examples for each category

---

## Summary

**What to Do**:
1. Edit product in admin
2. Find "Size Configuration" section
3. Add `selected_sizes` as JSON
4. Click Save
5. Done!

**Frontend Effect**:
- Only selected sizes appear
- Changes instant
- Sizes match what you set in admin

**Remember**:
- Sizes must exist in child category
- Use valid JSON format
- Shoe selector shown only for combos with shoe_sizes
- Leave empty = use all category sizes

---

Happy configuring! 🎉
