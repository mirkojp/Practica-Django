# Generated by Django 5.1.2 on 2024-10-12 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0002_alter_usuario_is_superuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reseña',
            name='funko',
        ),
    ]
