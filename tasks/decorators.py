from django.shortcuts import redirect
from functools import wraps
from .models import PerfilUsuario


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        try:
            usuario = PerfilUsuario.objects.get(id=user_id)
            request.user = usuario
            return view_func(request, *args, **kwargs)
        except PerfilUsuario.DoesNotExist:
            return redirect('login')
    return wrapper
