# Generated by Django 5.1.2 on 2025-03-27 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Direcciones', '0008_alter_provincia_idprovincia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provincia',
            name='idProvincia',
            field=models.CharField(max_length=1, primary_key=True, serialize=False),
        ),
    ]
