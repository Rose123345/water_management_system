from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse


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

STAFF_ROLE_NAMES = tuple(dict.fromkeys(role for roles in ROLE_ACCESS.values() for role in roles))

# Customers sign up from the public register page and only use the customer portal.
CUSTOMER_ROLE = 'Customer'

ROLE_NAMES = STAFF_ROLE_NAMES + (CUSTOMER_ROLE,)


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


def is_staff_member(user):
    return user.is_authenticated and in_groups(user, STAFF_ROLE_NAMES)


def is_customer(user):
    return (
        user.is_authenticated
        and not is_staff_member(user)
        and user.groups.filter(name=CUSTOMER_ROLE).exists()
    )


def home_url_for(user):
    """Where a signed-in user should land: the staff dashboard or the customer portal."""
    if is_customer(user):
        return reverse('portal:home')
    return reverse('dashboard:home')


def customer_required(view_func=None, *, require_profile=True):
    """Allow only customer accounts; send customers without a profile to complete it."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not is_customer(request.user):
                raise PermissionDenied
            if require_profile and not hasattr(request.user, 'customer_profile'):
                return redirect('portal:profile')
            return view_func(request, *args, **kwargs)

        return wrapped_view

    if view_func is not None:
        return decorator(view_func)
    return decorator
