# Generated by Django 5.1.2 on 2024-11-06 00:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Compras', '0007_carritoitem_subtotal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compra',
            name='carrito',
        ),
    ]
