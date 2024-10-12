from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from Productos.models import Funko


class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, password=None, **extra_fields):
        if not nombre:
            raise ValueError('El campo nombre debe estar presente')
        user = self.model(nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')

        return self.create_user(nombre, password, **extra_fields)



class Usuario(AbstractBaseUser, PermissionsMixin):
    idUsuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True, blank=False, null=False)  # Campo para autenticación
    contacto = PhoneNumberField(region="ES", null=True, blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Relaciones
    #favoritos = models.ManyToManyField(Funko, related_name='favoritos', blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre'  # Nombre se utiliza como campo para autenticación
    REQUIRED_FIELDS = []  # No hay campos requeridos adicionales

    # Ajustar related_name para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_groups',  # Cambia el nombre del accessor inverso
        blank=True,
        help_text="Los grupos a los que pertenece este usuario.",
        related_query_name='usuario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_user_permissions',  # Cambia el nombre del accessor inverso
        blank=True,
        help_text="Permisos específicos para este usuario.",
        related_query_name='usuario'
    )

    def __str__(self):
        return f'Nombre: {self.nombre}'
    
class Reseña(models.Model):
    idReseña = models.AutoField(primary_key=True)
    contenido = models.TextField()
    esetrellas = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    fecha = models.DateTimeField(auto_now_add=True)

    #Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    funko = models.ForeignKey(Funko,null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Reseña de {self.usuario.nombre} para {self.funko.nombre}'
