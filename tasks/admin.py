from django.contrib import admin
from .models import Categoria, Producto, PerfilUsuario


# Registra los modelos aqui...

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad_stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'telefono', 'direccion', 'date_joined']
    list_filter = ['date_joined', 'is_active']
    search_fields = ['username', 'email', 'telefono']

    def get_username(self, obj):
        return obj.username
    get_username.short_description = 'Nombre de Usuario'

    def get_email(self, obj):
        return obj.email
    get_email.short_description = 'Correo Electrónico'
