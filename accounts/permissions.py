from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


ROLE_ACCESS = {
    'customers': (
        'Administrator', 'Operations Manager', 'Customer Service Officer', 'Sales Officer',
    ),
    'products': (
        'Administrator', 'Operations Manager', 'Customer Service Officer', 'Sales Officer',
        'Production Officer', 'Inventory Officer', 'Distribution Officer',
    ),
    'production': ('Administrator', 'Operations Manager', 'Production Officer'),
    'inventory': ('Administrator', 'Operations Manager', 'Production Officer', 'Inventory Officer'),
    'sales': ('Administrator', 'Operations Manager', 'Sales Officer', 'Accountant'),
    'payments': ('Administrator', 'Sales Officer', 'Accountant'),
    'distribution': ('Administrator', 'Operations Manager', 'Distribution Officer', 'Sales Officer'),
    'expenses': ('Administrator', 'Accountant'),
    'dashboard': (
        'Administrator', 'Operations Manager', 'Customer Service Officer', 'Sales Officer',
        'Accountant', 'Production Officer', 'Inventory Officer', 'Distribution Officer',
    ),
    'reports': ('Administrator', 'Operations Manager', 'Accountant'),
}

ROLE_NAMES = tuple(dict.fromkeys(role for roles in ROLE_ACCESS.values() for role in roles))


def in_groups(user, group_names):
    return user.is_superuser or user.groups.filter(name__in=group_names).exists()


def role_required(*group_names):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not in_groups(request.user, group_names):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator