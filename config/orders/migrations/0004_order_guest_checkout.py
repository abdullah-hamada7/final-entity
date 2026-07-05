from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0003_cart_status_alter_cart_session_key_alter_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.TextField(blank=True, default='', verbose_name='العنوان'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
