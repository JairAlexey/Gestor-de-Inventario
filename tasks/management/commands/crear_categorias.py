from django.core.management.base import BaseCommand
from tasks.models import Categoria


class Command(BaseCommand):
    help = 'Crea las categorías predefinidas'

    def handle(self, *args, **kwargs):
        categorias = [
            {
                'nombre': 'Computadoras y Accesorios',
                'descripcion': 'Laptops, computadoras de escritorio y accesorios relacionados'
            },
            {
                'nombre': 'Smartphones y Tablets',
                'descripcion': 'Teléfonos móviles, tablets y accesorios'
            },
            {
                'nombre': 'Audio y Video',
                'descripcion': 'Equipos de sonido, video y accesorios multimedia'
            },
            {
                'nombre': 'Gaming',
                'descripcion': 'Consolas, videojuegos y accesorios para gaming'
            },
            {
                'nombre': 'Hogar Inteligente',
                'descripcion': 'Dispositivos y accesorios para automatización del hogar'
            },
            {
                'nombre': 'Almacenamiento y Periféricos',
                'descripcion': 'Discos duros, memorias USB y periféricos'
            },
            {
                'nombre': 'Redes y Conectividad',
                'descripcion': 'Routers, switches y equipos de red'
            },
            {
                'nombre': 'Drones y Gadgets',
                'descripcion': 'Drones y dispositivos tecnológicos innovadores'
            },
        ]

        for categoria in categorias:
            Categoria.objects.get_or_create(
                nombre=categoria['nombre'],
                defaults={'descripcion': categoria['descripcion']}
            )
            self.stdout.write(
                self.style.SUCCESS(f'Categoría "{categoria["nombre"]}" creada exitosamente')
            )
