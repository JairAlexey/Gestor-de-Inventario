from django.shortcuts import render, redirect, get_object_or_404
from .decorators import login_required
from .models import Producto, Categoria, PerfilUsuario
from django.contrib import messages
from .forms import ProductoForm, CategoriaForm
from django.db import transaction
from django import forms
from django.http import HttpResponse
from datetime import datetime
import csv  # <-- Para exportar CSV

# Importar LaunchDarkly
from feature_flags import is_feature_enabled


# Clase CSS reutilizable
INPUT_CLASS = (
    "appearance-none rounded-none relative block w-full px-3 py-2 border "
    "border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none "
    "focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
)


# =============================
#   DASHBOARD
# =============================
@login_required
def dashboard(request):

    # FLAGS correctos
    new_ui = is_feature_enabled("new-ui", request.user)
    dark_mode = is_feature_enabled("dark_mode", request.user)
    export_csv = is_feature_enabled("export_csv", request.user)

    print("🎯 FLAG new-ui:", new_ui)
    print("🌙 FLAG dark_mode:", dark_mode)
    print("📁 FLAG export_csv:", export_csv)

    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    productos_bajos = Producto.objects.filter(cantidad_stock__lte=5).count()

    categorias = Categoria.objects.all()
    form = ProductoForm()

    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'productos_bajos': productos_bajos,
        'form': form,
        'categorias': categorias,

        # === FLAGS CORRECTOS ===
        'new_ui': new_ui,
        'dark_mode': dark_mode,
        'export_csv': export_csv,
    }

    return render(request, 'dashboard.html', context)


# =============================
#   LISTADO DE PRODUCTOS / CRUD
# =============================
@login_required
def productos(request):
    productos_list = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos_list})


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
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
            usuario = PerfilUsuario.objects.get(username=username)
            if usuario.check_password(password):
                from django.contrib.auth import login as auth_login
                auth_login(request, usuario)
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

    return render(request, 'registration/login.html')


# =============================
#   FORMULARIO DE REGISTRO
# =============================
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


# =============================
#   CRUD PRODUCTOS
# =============================
@login_required
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('dashboard')
    else:
        form = ProductoForm()

    categorias = Categoria.objects.all()
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


# =============================
#   LISTA DE PRODUCTOS / CATEGORÍAS
# =============================
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
        'categoria_seleccionada': categoria_id,
        'url_limpiar': 'lista_productos'
    })


@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'productos/lista_categorias.html', {
        'categorias': categorias,
        'titulo': 'Lista de Categorías'
    })


@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'productos/crear_categoria.html', {
        'form': form
    })


# =============================
#   PDF REPORT
# =============================
@login_required
def generar_reporte_pdf(request):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        messages.error(request, 'La librería reportlab no está instalada.')
        return redirect('dashboard')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_productos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'

    productos = Producto.objects.all().select_related('categoria').order_by('categoria__nombre', 'nombre')

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    title = Paragraph("Reporte de Productos - Gestor de Inventario", title_style)
    elements.append(title)

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    info_text = f"<b>Fecha de generación:</b> {fecha}<br/><b>Total de productos:</b> {productos.count()}"
    info_para = Paragraph(info_text, styles['Normal'])
    elements.append(info_para)

    data = [['Nombre', 'Categoría', 'Stock', 'Precio', 'Descripción']]
    
    for p in productos:
        descripcion = p.descripcion[:50] + '...' if p.descripcion and len(p.descripcion) > 50 else (p.descripcion or 'Sin descripción')
        data.append([
            p.nombre,
            p.categoria.nombre,
            str(p.cantidad_stock),
            f"${p.precio:.2f}",
            descripcion
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ]))

    elements.append(table)
    doc.build(elements)
    return response


# =============================
#   PRODUCTOS BAJO STOCK
# =============================
@login_required
def productos_bajo_stock(request):
    categoria_id = request.GET.get('categoria')
    productos = Producto.objects.filter(cantidad_stock__lte=5).select_related('categoria').order_by('cantidad_stock')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    categorias = Categoria.objects.all()

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'titulo': 'Productos con Bajo Stock',
        'url_limpiar': 'productos_bajo_stock'
    })


# =============================
#   EXPORTAR CSV (NUEVA FEATURE FLAG)
# =============================
@login_required
def exportar_csv(request):
    if not is_feature_enabled("export_csv"):
        messages.error(request, "La función para exportar CSV no está habilitada.")
        return redirect("dashboard")

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="inventario_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Nombre", "Categoría", "Stock", "Precio", "Descripción"])

    productos = Producto.objects.all().select_related("categoria")

    for p in productos:
        writer.writerow([
            p.nombre,
            p.categoria.nombre,
            p.cantidad_stock,
            p.precio,
            p.descripcion if p.descripcion else "Sin descripción"
        ])

    return response