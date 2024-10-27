# Generated by Django 5.1.2 on 2024-10-27 21:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Compras', '0002_initial'),
        ('Productos', '0003_remove_funko_descuentos'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompraItem',
            fields=[
                ('idCompraItem', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Compras.compra')),
                ('funko', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Productos.funko')),
            ],
        ),
    ]
