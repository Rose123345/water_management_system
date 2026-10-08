from django.urls import reverse

from .permissions import ROLE_ACCESS, STAFF_ROLE_NAMES, is_customer


WORKSPACE_LINKS = (
    ('Overview', 'dashboard:home', 'dashboard', 'dashboard'),
    ('Customers', 'customers:list', 'customers', 'customers'),
    ('Products', 'products:list', 'products', 'products'),
    ('Production', 'production:list', 'production', 'production'),
    ('Inventory', 'inventory:list', 'inventory', 'inventory'),
    ('Orders', 'sales:list', 'sales', 'orders'),
    ('Deliveries', 'distribution:list', 'distribution', 'deliveries'),
    ('Expenses', 'expenses:list', 'expenses', 'expenses'),
    ('Reports', 'reports:index', 'reports', 'reports'),
)


CUSTOMER_LINKS = (
    ('My orders', 'portal:home', 'orders'),
    ('Products', 'portal:products', 'products'),
    ('Place an order', 'portal:order_add', 'inventory'),
    ('My details', 'portal:profile', 'customers'),
)


def workspace_navigation(request):
    user = request.user
    if not user.is_authenticated:
        return {
            'workspace_navigation': [],
            'workspace_home': reverse('accounts:login'),
            'is_customer_account': False,
        }

    if is_customer(user):
        return {
            'workspace_navigation': [
                {'label': label, 'path': reverse(url_name), 'icon': icon}
                for label, url_name, icon in CUSTOMER_LINKS
            ],
            'workspace_home': reverse('portal:home'),
            'is_customer_account': True,
            'account_role_label': 'Customer account',
        }

    role_names = set(user.groups.values_list('name', flat=True))
    if user.is_superuser:
        role_names.add('Administrator')
    staff_roles = sorted(role_names.intersection(STAFF_ROLE_NAMES))

    links = [
        {'label': label, 'path': reverse(url_name), 'icon': icon}
        for label, url_name, area, icon in WORKSPACE_LINKS
        if role_names.intersection(ROLE_ACCESS[area])
    ]
    return {
        'workspace_navigation': links,
        'workspace_home': reverse('dashboard:home'),
        'is_customer_account': False,
        'account_role_label': ', '.join(staff_roles) if staff_roles else 'No role assigned',
    }
