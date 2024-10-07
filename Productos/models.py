from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from num2words import num2words




class Categoría(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.nombre
    
class Descuento(models.Model):
    idDescuento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, editable=False, null=False, blank=False)
    porcentaje = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_expiracion = models.DateField(null=False, blank=False)

    def save(self, *args, **kwargs):
        # Convertir el porcentaje a texto y actualizar el campo nombre
        self.nombre = num2words(int(self.porcentaje), lang='es')  # Convertir a letras en español
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Descuento del {self.nombre} ({self.porcentaje}%)"

class Funko(models.Model):
    idFunko = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=False, null=False, unique=True)
    descripción = models.TextField(blank=False, null=False)
    is_backlight =  models.BooleanField(default=False, blank=False, null=False)
    stock = models.PositiveIntegerField(null=False, blank=False)
    precio = models.IntegerField()

    #Relaciones
    categoría = models.ManyToManyField(Categoría)
    descuentos = models.ManyToManyField('Descuento', through='FunkoDescuento', related_name='funkos')

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

    def clean(self):
        # Verificar que no haya otro descuento activo para este Funko en las fechas proporcionadas
        descuentos_activos = FunkoDescuento.objects.filter(
            funko=self.funko,
            fecha_expiracion__gte=self.fecha_inicio,
            fecha_inicio__lte=self.fecha_expiracion
        ).exclude(id=self.id)

        if descuentos_activos.exists():
            raise ValidationError("Ya existe un descuento vigente para este Funko en el período seleccionado.")

    def save(self, *args, **kwargs):
        # Ejecutar la validación antes de guardar
        self.clean()
        super().save(*args, **kwargs)


