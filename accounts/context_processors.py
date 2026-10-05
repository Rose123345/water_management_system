from django.urls import reverse

from .permissions import ROLE_ACCESS


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


def workspace_navigation(request):
    user = request.user
    if not user.is_authenticated:
        return {'workspace_navigation': []}

    role_names = set(user.groups.values_list('name', flat=True))
    if user.is_superuser:
        role_names.add('Administrator')

    links = [
        {'label': label, 'path': reverse(url_name), 'icon': icon}
        for label, url_name, area, icon in WORKSPACE_LINKS
        if role_names.intersection(ROLE_ACCESS[area])
    ]
    return {'workspace_navigation': links}