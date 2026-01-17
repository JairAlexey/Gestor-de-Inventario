#!/usr/bin/env python
"""Script para ejecutar migraciones en la base de datos de Railway."""
import os
import sys
import django

# Configurar el entorno para usar settings de producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_inventario.settings_production')

# Configurar Django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("🚀 Iniciando migraciones en Railway...\n")

    try:
        # Verificar conexión a la base de datos
        print("1️⃣ Verificando conexión a la base de datos...")
        call_command('check', '--database', 'default')
        print("✅ Conexión exitosa!\n")

        # Ejecutar migraciones
        print("2️⃣ Ejecutando migraciones...")
        call_command('migrate', '--noinput')
        print("✅ Migraciones completadas!\n")

        # Crear superusuario (opcional)
        print("3️⃣ ¿Deseas crear un superusuario? (y/n)")
        respuesta = input().strip().lower()
        if respuesta == 'y':
            call_command('createsuperuser')

        print("\n✅ ¡Proceso completado exitosamente!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
