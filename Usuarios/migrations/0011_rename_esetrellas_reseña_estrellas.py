# Generated by Django 5.1.2 on 2025-03-16 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0010_alter_usuario_contacto'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reseña',
            old_name='esetrellas',
            new_name='estrellas',
        ),
    ]
