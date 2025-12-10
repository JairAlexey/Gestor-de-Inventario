from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.

class Categoria(models.Model):
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class PerfilUsuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

    # Agregar related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='perfil_usuarios',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.',
        verbose_name='grupos'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='perfil_usuarios',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='permisos de usuario'
    )

    class Meta:
        db_table = 'perfil_usuario'

    def __str__(self):
        return f"{self.username} - {self.email}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
