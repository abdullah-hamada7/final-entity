from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_guest_checkout'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='unit_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name='سعر الوحدة',
            ),
        ),
    ]
