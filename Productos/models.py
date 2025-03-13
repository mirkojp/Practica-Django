from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from num2words import num2words
from .services import delete_image_from_cloudinary

class Imagen(models.Model):
    idImagen = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=100, help_text="Identificador en Cloudinary o S3")
    url = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100, help_text="Nombre original de la imagen")
    ancho = models.IntegerField()
    alto = models.IntegerField()
    formato = models.CharField(max_length=10)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.idImagen})"


class Categoría(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.nombre

class Descuento(models.Model):
    idDescuento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False, blank=False, unique=True)
    porcentaje = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0), MaxValueValidator(100)])

    #def save(self, *args, **kwargs):
        # Convertir el porcentaje a texto y actualizar el campo nombre
        #self.nombre = num2words(int(self.porcentaje), lang='es')  # Convertir a letras en español
        #super().save(*args, **kwargs)

    def __str__(self):
        return f"Descuento del {self.nombre} ({self.porcentaje}%)"


class Funko(models.Model):
    idFunko = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=False, null=False, unique=True)
    descripción = models.TextField(blank=False, null=False)
    is_backlight = models.BooleanField(default=False, blank=False, null=False)
    stock = models.PositiveIntegerField(null=False, blank=False)
    precio = models.IntegerField()

    # Relaciones
    categoría = models.ManyToManyField(Categoría)
    imagen = models.OneToOneField(
        Imagen, on_delete=models.SET_NULL, null=True, blank=True
    )  # Si se elimina la imagen, el Funko no se borra

    def delete(self, *args, **kwargs):
        """Borra la imagen en Cloudinary antes de eliminar el Funko"""
        if self.imagen:
            delete_image_from_cloudinary(self.imagen.clave)  # Elimina de Cloudinary
            self.imagen.delete()  # Elimina de la BD

        super().delete(*args, **kwargs)  # Borra el Funko de la BD

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock} - Precio: {self.precio}"


class FunkoDescuento(models.Model):
    idFunkoDescuento = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_expiracion = models.DateField(null=False, blank=False)
    #Relaciones
    funko = models.ForeignKey(Funko, on_delete=models.CASCADE)
    descuento = models.ForeignKey(Descuento, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('funko', 'descuento', 'fecha_inicio', 'fecha_expiracion')


    def save(self, *args, **kwargs):
        # Ejecutar la validación antes de guardar
        super().save(*args, **kwargs)
