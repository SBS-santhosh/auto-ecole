from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def role_required(role):
    """Décorateur pour restreindre l'accès selon le rôle."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Veuillez vous connecter.")
                return redirect('connexion')
            try:
                profile = request.user.profile
            except Exception:
                messages.error(request, "Profil non trouvé.")
                return redirect('connexion')
            if profile.role != role and not request.user.is_superuser:
                messages.error(request, "Vous n'avez pas accès à cette page.")
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def eleve_required(view_func):
    """Restreindre l'accès aux élèves."""
    return role_required('eleve')(view_func)


def moniteur_required(view_func):
    """Restreindre l'accès aux moniteurs."""
    return role_required('moniteur')(view_func)


def admin_required(view_func):
    """Restreindre l'accès aux administrateurs."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('connexion')
        try:
            profile = request.user.profile
            is_admin = profile.role == 'admin'
        except Exception:
            is_admin = False
        if not is_admin and not request.user.is_superuser:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper
