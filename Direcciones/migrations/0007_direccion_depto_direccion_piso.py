# Generated by Django 5.1.2 on 2025-03-26 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Direcciones', '0006_delete_dirección'),
    ]

    operations = [
        migrations.AddField(
            model_name='direccion',
            name='depto',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='direccion',
            name='piso',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
