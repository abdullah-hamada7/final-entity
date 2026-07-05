from django.db import migrations


def force_fix_category_icons(apps, schema_editor):
    Category = apps.get_model('products', 'Category')

    slug_icons = {
        'surgical-equipment': 'fas fa-scissors',
        'care-devices': 'fas fa-heart-pulse',
        'medical-care': 'fas fa-heart-pulse',
        'medical-devices': 'fas fa-stethoscope',
        'medical-supplies': 'fas fa-medkit',
        'endoscopy': 'fas fa-stethoscope',
    }

    for category in Category.objects.all():
        name = category.name or ''
        slug = category.slug or ''
        icon = None

        if 'جراح' in name:
            icon = 'fas fa-scissors'
        elif 'رعاية' in name:
            icon = 'fas fa-heart-pulse'
        elif 'منظار' in name or 'مناظير' in name:
            icon = 'fas fa-stethoscope'
        elif 'مستلزم' in name:
            icon = 'fas fa-medkit'
        elif slug in slug_icons:
            icon = slug_icons[slug]

        if icon and category.icon != icon:
            category.icon = icon
            category.save(update_fields=['icon'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_category_icons'),
    ]

    operations = [
        migrations.RunPython(force_fix_category_icons, migrations.RunPython.noop),
    ]
