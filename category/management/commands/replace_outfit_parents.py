from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime


class Command(BaseCommand):
    help = 'Replace Outfit parent with Upper and Lower; delete Outfit children and related products. Backups DB first.'

    def handle(self, *args, **options):
        # Backup sqlite DB if present
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        if os.path.exists(db_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(settings.BASE_DIR, f'db.sqlite3.backup.{ts}')
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'Backup created: {backup_path}'))
        else:
            self.stdout.write(self.style.WARNING('No db.sqlite3 found to backup'))

        # Import models (after Django setup)
        from category.models import ParentCategory, ChildCategory
        from store.models import Product

        # Ensure Upper and Lower parent categories exist
        created = []
        for key, name, slug in [('upper', 'Upper', 'upper'), ('lower', 'Lower', 'lower')]:
            pc, was_created = ParentCategory.objects.get_or_create(key=key, defaults={'name': name, 'slug': slug})
            if was_created:
                created.append(pc)
                self.stdout.write(self.style.SUCCESS(f'Created ParentCategory: {key}'))

        # Find any Outfit parent entries (by key/name/slug)
        outfit_qs = ParentCategory.objects.filter(key__iexact='outfit') | ParentCategory.objects.filter(name__iexact='outfit') | ParentCategory.objects.filter(slug__iexact='outfit')
        outfit_qs = outfit_qs.distinct()

        total_products_deleted = 0
        total_children_deleted = 0
        total_parents_deleted = 0

        if outfit_qs.exists():
            for outfit in outfit_qs:
                self.stdout.write(f'Processing Outfit parent: id={outfit.id} name={outfit.name} key={outfit.key}')
                children = ChildCategory.objects.filter(parent=outfit)
                for child in children:
                    # Delete products linked to this child category
                    prod_qs = Product.objects.filter(child_category=child)
                    nprod = prod_qs.count()
                    if nprod:
                        prod_qs.delete()
                        total_products_deleted += nprod
                        self.stdout.write(self.style.SUCCESS(f'Deleted {nprod} products for child category {child}'))
                    # Delete the child category
                    child.delete()
                    total_children_deleted += 1
                    self.stdout.write(self.style.SUCCESS(f'Deleted child category {child.name}'))

                # after children removed, delete the parent
                outfit.delete()
                total_parents_deleted += 1
                self.stdout.write(self.style.SUCCESS(f'Deleted Outfit parent {outfit.name}'))
        else:
            self.stdout.write(self.style.NOTICE('No Outfit parent categories found'))

        self.stdout.write(self.style.SUCCESS(f'Total products deleted: {total_products_deleted}'))
        self.stdout.write(self.style.SUCCESS(f'Total child categories deleted: {total_children_deleted}'))
        self.stdout.write(self.style.SUCCESS(f'Total parent categories deleted: {total_parents_deleted}'))

        self.stdout.write(self.style.SUCCESS('Operation complete. Please restart server and verify admin UI.'))
