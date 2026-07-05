from django.db import migrations


SLUG_ICONS = {
    'surgical-equipment': 'fas fa-scissors',
    'care-devices': 'fas fa-heart-pulse',
    'medical-care': 'fas fa-heart-pulse',
    'medical-devices': 'fas fa-stethoscope',
    'medical-supplies': 'fas fa-medkit',
    'endoscopy': 'fas fa-stethoscope',
}


def set_category_icons(apps, schema_editor):
    Category = apps.get_model('products', 'Category')

    for category in Category.objects.all():
        raw = (category.icon or '').strip()
        if raw and 'fa-' in raw and raw.split()[0] in ('fas', 'far', 'fab', 'fa'):
            continue

        updated = None
        if category.slug in SLUG_ICONS:
            updated = SLUG_ICONS[category.slug]
        elif 'جراح' in (category.name or ''):
            updated = 'fas fa-scissors'
        elif 'رعاية' in (category.name or ''):
            updated = 'fas fa-heart-pulse'
        elif 'منظار' in (category.name or '') or 'مناظير' in (category.name or ''):
            updated = 'fas fa-stethoscope'
        elif 'مستلزم' in (category.name or ''):
            updated = 'fas fa-medkit'
        elif not raw or 'fa-' not in raw:
            updated = 'fas fa-folder'

        if updated and category.icon != updated:
            category.icon = updated
            category.save(update_fields=['icon'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(set_category_icons, migrations.RunPython.noop),
    ]
