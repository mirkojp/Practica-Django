from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Provincia(models.Model):
    idProvincia = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    idCiudad = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    # Relaciones
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.nombre}'

class Dirección(models.Model):
    idDireccion = models.AutoField(primary_key=True)
    calle = models.CharField(max_length=100, null=False, blank=False)
    numero = models.PositiveIntegerField(null=False, blank=False)
    contacto = PhoneNumberField(region="AR", null=True, blank=True) 
    email = models.EmailField(null=False, blank=False)
    codigo_postal = models.CharField(max_length=10,default="0000", null=False, blank=False)

    # Relaciones
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, null=False, blank=False)

    def __str__(self):
        return f"Dirección {self.calle}, {self.numero}, Email: {self.email}, Ciudad: {self.ciudad}"
