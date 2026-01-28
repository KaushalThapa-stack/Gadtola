from category.models import Category, ParentCategory


def menu_links(request):
    # Get parent categories for navbar
    parent_categories = ParentCategory.objects.all().order_by('name')
    # Also keep legacy categories for backward compatibility
    links = Category.objects.all()
    return dict(links=links, parent_links=parent_categories)