from django.shortcuts import render, redirect, get_object_or_404
from .decorators import login_required
from .models import Producto, Categoria, PerfilUsuario
from django.contrib import messages
from .forms import ProductoForm
from django.db import transaction
from django import forms


# Clase CSS reutilizable para widgets (evita líneas demasiado largas)
INPUT_CLASS = (
    "appearance-none rounded-none relative block w-full px-3 py-2 border "
    "border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none "
    "focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
)


@login_required
def dashboard(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    productos_bajos = Producto.objects.filter(cantidad_stock__lte=10).count()

    # Obtener todas las categorías
    categorias = Categoria.objects.all()
    form = ProductoForm()

    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'productos_bajos': productos_bajos,
        'form': form,
        'categorias': categorias,  # Añadimos las categorías al contexto
    }
    return render(request, 'dashboard.html', context)


@login_required
def productos(request):
    productos_list = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos_list})


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        # Validación de contraseñas iguales
        if form.is_valid():
            if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                form.add_error('password2', 'Las contraseñas no coinciden')
            else:
                try:
                    with transaction.atomic():
                        usuario = PerfilUsuario(
                            username=form.cleaned_data['username'],
                            email=form.cleaned_data['email'],
                            telefono=form.cleaned_data['telefono'],
                            direccion=form.cleaned_data['direccion']
                        )
                        usuario.set_password(form.cleaned_data['password1'])
                        usuario.save()

                        request.session['user_id'] = usuario.id
                        messages.success(request, f'¡Bienvenido {usuario.username}!')
                        return redirect('dashboard')
                except Exception as e:
                    messages.error(request, f'Error al crear el usuario: {str(e)}')
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Primero, obtén el usuario por nombre de usuario
            usuario = PerfilUsuario.objects.get(username=username)
            # Luego verifica la contraseña
            if usuario.check_password(password):
                # Si la contraseña es correcta, inicia sesión
                from django.contrib.auth import login as auth_login
                auth_login(request, usuario)
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

    return render(request, 'registration/login.html')


class RegistroForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Nombre de usuario'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Correo electrónico'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Contraseña'
        }),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Confirmar contraseña'
        }),
        required=True
    )
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Teléfono'
        })
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Dirección',
            'rows': '3'
        })
    )


@login_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('dashboard')  # Redirigir al dashboard en lugar de productos
    else:
        form = ProductoForm()

    categorias = Categoria.objects.all()  # Obtener todas las categorías
    return render(request, 'productos/crear.html', {
        'form': form,
        'categorias': categorias
    })


@login_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar.html', {'form': form, 'producto': producto})


@login_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('lista_productos')
    return render(request, 'productos/eliminar.html', {'producto': producto})


@login_required
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/detalle.html', {'producto': producto})


@login_required
def lista_productos(request):
    categoria_id = request.GET.get('categoria')
    productos = Producto.objects.all().select_related('categoria')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    categorias = Categoria.objects.all()

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id
    })


@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'productos/lista_categorias.html', {
        'categorias': categorias,
        'titulo': 'Lista de Categorías'
    })


@login_required
def productos_bajo_stock(request):
    productos = Producto.objects.filter(cantidad_stock__lte=10).order_by('cantidad_stock')
    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'titulo': 'Productos con Bajo Stock'
    })