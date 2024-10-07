from django.db import models
from Usuarios.models import Usuario
from Productos.models import Funko
from Direcciones.models import Dirección


# Create your models here.

class Carrito(models.Model):
    idCarrito = models.AutoField(primary_key=True)
    total = models.PositiveIntegerField(default=0, blank=True)

    #Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    #funkos = models.ManyToManyField(Funko, blank=True)

    def __str__(self):
        return f"Carrito {self.idCarrito} - Total: {self.total}"

class CarritoItem(models.Model):
    idCarritoItem = models.AutoField(primary_key=True)
    cantidad = models.PositiveIntegerField(default=1)

    #Relaciones
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    funko = models.ForeignKey(Funko, on_delete=models.CASCADE)
    
    def subtotal(self):
        return self.funko.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.funko.nombre}"


class Compra(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADA', 'Enviada'),
        ('ENTREGADA', 'Entregada'),
    ]

    idCompra = models.AutoField(primary_key=True)
    subtotal = models.PositiveIntegerField(null=False, blank=False)
    total = models.PositiveIntegerField(null=False, blank=False)
    fecha = models.DateField(null=False, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)

    #Relaciones
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    carrito = models.OneToOneField(Carrito, on_delete=models.PROTECT)
    direccion = models.ForeignKey(Dirección, on_delete=models.PROTECT, null=False, blank=False)

    def __str__(self):
        return f"Compra {self.id} - Estado: {self.estado} - Total: {self.total}"
