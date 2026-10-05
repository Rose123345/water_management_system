# WMDMS Roles

## First-time setup

Run these commands from the `WMDMS` project directory:

```powershell
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
```

Sign in to `/admin/` with the superuser. In **Users**, set a user's **Groups** to the role that matches their job. New self-registered accounts receive no role automatically and cannot open operational pages until an administrator assigns one. Superusers bypass role checks.

Run `python manage.py setup_roles` again at any time to restore any missing role groups; it does not remove or change existing group memberships.

## Roles and access

| Role | Workspace areas |
| --- | --- |
| Administrator | All areas; can manage products and orders |
| Operations Manager | Dashboard, customers, products, production, inventory, orders, deliveries, reports |
| Customer Service Officer | Dashboard, customers, products |
| Sales Officer | Dashboard, customers, products, orders, payments, deliveries |
| Accountant | Dashboard, orders, payments, expenses, reports |
| Production Officer | Dashboard, products, production, inventory |
| Inventory Officer | Dashboard, products, inventory |
| Distribution Officer | Dashboard, products, deliveries |

Only Administrators can add, edit, activate, or deactivate products. Sales Officers and Administrators can create and update orders. Public home, about, contact, and product catalogue pages remain available without a staff role.
