from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# class Ciudad(models.Model):
#     idCiudad = models.IntegerField(primary_key=True)
#     nombre = models.CharField(max_length=100)

#     # Relaciones
#     provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)

#     def __str__(self):
#         return f'{self.nombre}'

# class Dirección(models.Model):
#     idDireccion = models.AutoField(primary_key=True)
#     calle = models.CharField(max_length=100, null=False, blank=False)
#     numero = models.PositiveIntegerField(null=False, blank=False)
#     contacto = PhoneNumberField(region="AR", null=True, blank=True)
#     email = models.EmailField(null=False, blank=False)
#     codigo_postal = models.CharField(max_length=10,default="0000", null=False, blank=False)

#     # Relaciones
#     ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, null=False, blank=False)

#     def __str__(self):
#         return f"Dirección {self.calle}, {self.numero}, Email: {self.email}, Ciudad: {self.ciudad}"


from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Provincia(models.Model):
    idProvincia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    idCiudad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    provincia = models.ForeignKey(
        Provincia, on_delete=models.CASCADE, related_name="ciudades"
    )

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"


class Coordenada(models.Model):
    idCoordenada = models.AutoField(primary_key=True)
    latitud = models.DecimalField(max_digits=32, decimal_places=8)
    longitud = models.DecimalField(max_digits=32, decimal_places=8)

    def __str__(self):
        return f"({self.latitud}, {self.longitud})"


class Direccion(models.Model):
    idDireccion = models.AutoField(primary_key=True)
    calle = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    depto = models.CharField(max_length=10, blank=True, null=True)
    piso = models.CharField(max_length=10, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20)
    contacto = PhoneNumberField(region="AR", null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    coordenada = models.OneToOneField(
        Coordenada, on_delete=models.CASCADE, related_name="direccion"
    )
    ciudad = models.ForeignKey(
        Ciudad, on_delete=models.CASCADE, related_name="direcciones"
    )

    def __str__(self):
        return f"{self.calle} {self.numero}{' Piso ' + self.piso if self.piso else ''}{' Depto ' + self.depto if self.depto else ''}, {self.ciudad.nombre} ({self.codigo_postal})"
