"""
URL configuration for gestor_inventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('productos-bajo-stock/', views.productos_bajo_stock, name='productos_bajo_stock'),
]
