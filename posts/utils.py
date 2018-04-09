from rest_framework.generics import GenericAPIView
from rest_framework import serializers

class FieldSelectableAPIView(GenericAPIView):
	included_fields_query_param = 'fields'
	excluded_fields_query_param = 'ex_fields'
	def get_serializer(self, *args, **kwargs):
		"""
		Returns the serializer context with the 'fields' key populated by
		the `fields` and `ex_fields` provided in the request's query parameters. 
		"""
		serializer_class = self.get_serializer_class()
		kwargs['context'] = self.get_serializer_context()
		kwargs['fields'] = self.request.query_params.getlist(self.included_fields_query_param, None)
		return serializer_class(*args, **kwargs)

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
	"""
	A ModelSerializer that takes an additional `fields` argument that
	controls which fields should be displayed.
	"""

	def __init__(self, *args, **kwargs):
		# Don't pass the 'fields' arg up to the superclass
		fields = kwargs.pop('fields', [])
		ex_fields = kwargs.pop('ex_fields', [])
		# Instantiate the superclass normally
		super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

		if len(fields) > 0:
			# Drop any fields that are not specified in the `fields` argument.
			allowed = set(fields)
			existing = set(self.fields)
			for field_name in existing - allowed:
				self.fields.pop(field_name)

	