from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Fix category icons for Font Awesome 6 (surgical, care, etc.)'

    def handle(self, *args, **options):
        updated = 0
        for category in Category.objects.all():
            icon = category.display_icon
            if category.icon != icon:
                self.stdout.write(f'{category.name}: {category.icon!r} -> {icon!r}')
                category.icon = icon
                category.save(update_fields=['icon'])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} categor{"y" if updated == 1 else "ies"}.'))
