# Generated by Django 5.1.2 on 2024-10-24 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Direcciones', '0003_alter_dirección_contacto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ciudad',
            name='idCiudad',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='idProvincia',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
