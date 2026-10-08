from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from customers.models import Customer
from Inventory.models import StockMovement
from Inventory.services import record_stock_movement
from products.models import Product

from .models import Order, OrderItem


def make_user(username, *roles):
	user = get_user_model().objects.create_user(username=username, password='safe-test-password')
	for role in roles:
		user.groups.add(Group.objects.get_or_create(name=role)[0])
	return user


def make_product(name='Spring 500ml', price='5.00', stock=0, **kwargs):
	product = Product.objects.create(
		name=name, product_type=Product.ProductType.BOTTLED,
		package_size='500ml', unit_price=price, **kwargs,
	)
	if stock:
		record_stock_movement(product, StockMovement.MovementType.RECEIPT, stock)
	return product


def make_order(customer=None, product=None, quantity=2, status=Order.Status.PENDING):
	customer = customer or Customer.objects.create(name='Test Customer', phone='0240000000')
	product = product or make_product(stock=100)
	order = Order.objects.create(customer=customer)
	OrderItem.objects.create(order=order, product=product, quantity=quantity)
	if status != Order.Status.PENDING:
		Order.objects.filter(pk=order.pk).update(status=status)
		order.refresh_from_db()
	return order
