from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.productos, name='productos'),
    path('producto/crear/', views.producto_crear, name='producto_crear'),
    path('producto/editar/<int:pk>/', views.producto_editar, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.producto_eliminar, name='eliminar_producto'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('lista-productos/', views.lista_productos, name='lista_productos'),
    path('lista-categorias/', views.lista_categorias, name='lista_categorias'),
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
    path('productos-bajo-stock/', views.productos_bajo_stock, name='productos_bajo_stock'),
    path('reporte-pdf/', views.generar_reporte_pdf, name='reporte_pdf'),
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),

]