import pytest
from django.test import Client
from django.urls import reverse
from tasks.models import PerfilUsuario, Categoria, Producto
from tasks.forms import ProductoForm

@pytest.mark.django_db
class TestPublicViews:
    """Tests para vistas públicas del sistema"""
    
    def test_registro_view_accessible(self):
        """Verifica que la vista de registro sea accesible sin autenticación"""
        client = Client()
        response = client.get(reverse('registro'))
        
        assert response.status_code == 200
        assert 'registro' in response.content.decode().lower()
    
    def test_login_view_accessible(self):
        """Verifica que la vista de login sea accesible sin autenticación"""
        client = Client()
        response = client.get(reverse('login'))
        
        assert response.status_code == 200

    def test_dashboard_requires_login(self):
        """Dashboard debe requerir autenticación"""
        client = Client()
        resp = client.get(reverse('dashboard'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_registro_form_validation(self):
        """El formulario de registro valida contraseñas distintas"""
        client = Client()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'abc12345',
            'password2': 'diferente',
        }
        resp = client.post(reverse('registro'), data)
        assert resp.status_code == 200
        assert "corregir" in resp.content.decode().lower() or "error" in resp.content.decode().lower()

    def test_login_invalid_credentials(self):
        """Login rechaza credenciales inválidas"""
        client = Client()
        resp = client.post(reverse('login'), {'username': 'noexiste', 'password': 'incorrecta'})
        assert resp.status_code == 200
        assert "usuario no encontrado" in resp.content.decode().lower() or "contraseña incorrecta" in resp.content.decode().lower()


@pytest.mark.django_db
class TestProtectedViews:
    """Tests para vistas protegidas"""

    def setup_method(self):
        self.user = PerfilUsuario.objects.create(username="usuario", email="u@e.com")
        self.user.set_password("abc12345")
        self.user.save()
        self.client = Client()
        # Login manual (simula decorador)
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

    def test_dashboard_authenticated(self):
        resp = self.client.get(reverse('dashboard'))
        assert resp.status_code == 200
        assert "dashboard" in resp.content.decode().lower()

    def test_lista_productos_authenticated(self):
        resp = self.client.get(reverse('lista_productos'))
        assert resp.status_code == 200
        assert "producto" in resp.content.decode().lower()

    def test_productos_bajo_stock(self):
        cat = Categoria.objects.create(nombre="Cat", descripcion="desc")
        Producto.objects.create(nombre="P1", descripcion="d", precio=1, cantidad_stock=5, categoria=cat)
        resp = self.client.get(reverse('productos_bajo_stock'))
        assert resp.status_code == 200
        assert "bajo stock" in resp.content.decode().lower()

    def test_protected_view_redirects_without_login(self):
        client = Client()
        resp = client.get(reverse('dashboard'))
        assert resp.status_code == 302
        assert reverse('login') in resp.url

@pytest.mark.django_db
def test_producto_form_validation():
    """El formulario de producto valida campos requeridos"""
    cat = Categoria.objects.create(nombre="Cat", descripcion="desc")
    form = ProductoForm(data={
        'nombre': '',
        'descripcion': 'desc',
        'precio': '',
        'cantidad_stock': '',
        'categoria': cat.id,
    })
    assert not form.is_valid()
    assert 'nombre' in form.errors
    assert 'precio' in form.errors
    assert 'cantidad_stock' in form.errors

@pytest.mark.django_db
def test_producto_model_str_and_methods():
    """Métodos de modelo Producto y Categoria"""
    cat = Categoria.objects.create(nombre="Cat", descripcion="desc")
    prod = Producto.objects.create(nombre="P", descripcion="d", precio=1, cantidad_stock=1, categoria=cat)
    assert str(cat) == "Cat"
    assert str(prod) == "P"

@pytest.mark.django_db
def test_perfilusuario_set_and_check_password():
    """Métodos de set_password y check_password en PerfilUsuario"""
    user = PerfilUsuario(username="u", email="e@e.com")
    user.set_password("clave123")
    assert user.check_password("clave123")
    assert not user.check_password("otra")

