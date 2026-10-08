class RecordedByAdminMixin:
	"""Fill a "created by"-style user field with the signed-in admin instead of a dropdown."""

	recorded_by_field = 'created_by'

	def get_readonly_fields(self, request, obj=None):
		readonly = tuple(super().get_readonly_fields(request, obj))
		if self.recorded_by_field not in readonly:
			readonly += (self.recorded_by_field,)
		return readonly

	def save_model(self, request, obj, form, change):
		if not change and not getattr(obj, f'{self.recorded_by_field}_id'):
			setattr(obj, self.recorded_by_field, request.user)
		super().save_model(request, obj, form, change)
