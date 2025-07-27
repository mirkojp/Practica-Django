from django.db import models
from Usuarios.models import Usuario
from Productos.models import Funko
from Direcciones.models import Direccion
from django.core.validators import MinValueValidator

# Create your models here.

class Carrito(models.Model):
    idCarrito = models.AutoField(primary_key=True)
    total = models.FloatField(
        default=0, blank=True, validators=[MinValueValidator(0.0)]
    )
    envio = models.FloatField(default=0, blank=True, validators=[MinValueValidator(0.0)])

    # Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Carrito {self.idCarrito} - Total: {self.total}"

class CarritoItem(models.Model):
    idCarritoItem = models.AutoField(primary_key=True)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.FloatField(
        default=0, blank=True, validators=[MinValueValidator(0.0)]
    )

    # Relaciones
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    funko = models.ForeignKey(Funko, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cantidad} x {self.funko.nombre}"


class Compra(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADA', 'Enviada'),
        ('ENTREGADA', 'Entregada'),
    ]

    idCompra = models.AutoField(primary_key=True)
    subtotal = models.FloatField(
        default=0, blank=True, validators=[MinValueValidator(0.0)]
    )
    total = models.FloatField(
        default=0, blank=True, validators=[MinValueValidator(0.0)]
    )
    fecha = models.DateField(null=False, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    envio = models.FloatField(default=0, blank=True, validators=[MinValueValidator(0.0)])
    # Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT, null=False, blank=False)

    def __str__(self):
        return f"Compra {self.id} - Estado: {self.estado} - Total: {self.total}"


class CompraItem(models.Model):
    idCompraItem = models.AutoField(primary_key=True)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.FloatField(
        default=0, blank=True, validators=[MinValueValidator(0.0)]
    )

    # Relaciones
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="items")
    funko = models.ForeignKey(Funko, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cantidad} x {self.funko.nombre} - Subtotal {self.subtotal} - Compra {self.compra.idCompra}"
