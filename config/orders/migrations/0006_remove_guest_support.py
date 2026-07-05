from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def remove_guest_records(apps, schema_editor):
    Cart = apps.get_model('orders', 'Cart')
    Order = apps.get_model('orders', 'Order')
    Cart.objects.filter(user__isnull=True).delete()
    Order.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0005_cartitem_unit_price'),
    ]

    operations = [
        migrations.RunPython(remove_guest_records, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='cart',
            name='session_key',
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='carts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
