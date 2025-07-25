# Generated by Django 5.2.3 on 2025-07-04 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_shippingaddress_shipping_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='strip_token',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
