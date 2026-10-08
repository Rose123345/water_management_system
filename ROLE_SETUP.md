# WMDMS Roles

## First-time setup

Run these commands from the `WMDMS` project directory:

```powershell
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
```

Sign in to `/admin/` with the superuser. In **Users**, set a user's **Groups** to the role that matches their job. Accounts created from the public register page automatically receive the **Customer** role and a linked customer record; they only use the customer portal at `/my-account/`. Staff accounts must be created by an administrator with the right role. Superusers bypass role checks.

To give an existing customer record a login, create the user with the **Customer** role, then open the customer in **Customers** in the admin and set its **User**. A customer user without a linked record is asked to fill in their details the first time they sign in.

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
| Customer | Customer portal only: place orders, view own orders, payments and deliveries |

Only Administrators can add, edit, activate, or deactivate products. Sales Officers and Administrators can create, confirm, complete and cancel orders, including orders customers place from the portal. Only Distribution Officers can be assigned deliveries. Public home, about, contact, and product catalogue pages remain available without a staff role.
