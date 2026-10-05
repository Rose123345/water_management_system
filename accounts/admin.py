from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm
from django.contrib.auth.models import Group

from .permissions import ROLE_NAMES


class RoleUserCreationForm(AdminUserCreationForm):
	groups = forms.ModelMultipleChoiceField(
		queryset=Group.objects.filter(name__in=ROLE_NAMES).order_by('name'),
		required=False,
		label='Roles',
		help_text='Select the role or roles this user should have.',
	)

	class Meta(AdminUserCreationForm.Meta):
		fields = ('username', 'groups')


class RoleUserAdmin(UserAdmin):
	add_form = RoleUserCreationForm
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'password1', 'password2', 'groups'),
		}),
	)
	filter_horizontal = ('groups', 'user_permissions')


User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, RoleUserAdmin)
