from django.shortcuts import render, get_object_or_404
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from posts.models import Post, PostImage, Category, CategoryAttribute
from posts.serializers import PostSerializer, CategorySerializer, PostPhotoSerializer
from posts.utils import FieldSelectableAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.pagination import PageNumberPagination
from functools import reduce 

class PostCreateView(generics.ListCreateAPIView, FieldSelectableAPIView):
	queryset = Post.objects.all()
	serializer_class = PostSerializer
	permission_classes = (IsAuthenticated, )

	def get_queryset(self):
		user = self.request.user
		return Post.objects.filter(poster=user)
	
	def perform_create(self, serializer):
		serializer.save(poster=self.request.user)

class PostRetrieveView(generics.RetrieveAPIView, FieldSelectableAPIView):
	queryset = Post.objects.all()
	serializer_class = PostSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser,])
def post_photo_create_view(request, pk):
	post = get_object_or_404(Post, pk=pk)
	image = request.data.pop('image', [])
	images = []
	for img in image:
		photo = PostImage.objects.create(image=img, post=post)
		images.append(photo)
	serializer = PostPhotoSerializer(images, many=True)
	return Response(serializer.data)

class CategoryListView(generics.ListAPIView, FieldSelectableAPIView):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer 
	pagination_class = None

class CategoryRetrieveView(generics.RetrieveAPIView, FieldSelectableAPIView):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

class SearchView(generics.ListAPIView, FieldSelectableAPIView):
	serializer_class = PostSerializer

	def list(self, request, *args, **kwargs):
		# OVERRIDING rest_framework.mixins.ListView list() method 
		# Using this method hook to inject faceted information about category results
		queryset = self.filter_queryset(self.get_queryset())
		categories = Category.objects.all()
		cat_id = request.query_params.get('cat', None)
		if cat_id is not None:
			categories = Category.objects.get(pk=request.query_params.get('cat')).get_all_sub_categories()

		category_counts = {}
		for cat in categories:
			category_counts[cat.pk] = {
				'category': {
					'short_name': cat.pk,
					'name': cat.name
				},
				'count': 0
			}

		for post in queryset:
			category_counts[post.category.pk]['count'] += 1

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			response = self.get_paginated_response(serializer.data)
			response.data['category_counts'] = category_counts
			return response 

		serializer = self.get_serializer(queryset, many=True)
		response = Response(data)
		response.data['category_counts'] = category_counts
		return response

	def get_queryset(self):
		query_params = self.request.query_params.copy()
		return generate_qs(query_params)

def generate_qs(query_params):
	# Query params are parsed as list
	cat_id = query_params.pop('cat', [None])[0]
	ex_cats = query_params.pop('ex_cats', None)
	qs = Post.objects.all()

	text = query_params.pop('text', None)
	if text and len(text[0]) > 0:
		if isinstance(text, list):
			text = reduce(lambda x, y: '{0} {1}'.format(x, y), text)
		qs = qs.annotate(
			search=SearchVector('title', 'detail')	
		).filter(search=text)

	if cat_id is not None:
		category = get_object_or_404(Category, pk=cat_id)
		cat_attributes = list(category.get_all_attributes())
		qs = qs.filter(category__in=category.get_all_sub_categories())
		for param in query_params:
			qs = qs & parse_category_filter_from_query_param(param, query_params, cat_attributes)

	if ex_cats is not None:
		qs = qs.exclude(category__pk__in=ex_cats)

	print(qs.query)
	return qs

def parse_category_filter_from_query_param(param, query_params, category_attributes):
	# Sanity checks
	assert param is not None, (
			"You passed in an empty param. You must pass in a param and query_params"
		)
	assert query_params is not None, (
			"You passed in an empty param value. You must pass in a param and query_params"
		)
	assert category_attributes is not None, (
			"You passed in a null category_attributes object."
		)

	assert isinstance(category_attributes, list), (
			"You passed in {0} for category_attributes which is not of type list."
		)

	assert all(isinstance(x, CategoryAttribute) for x in category_attributes), (
			"You passed in a list that does not contain all CategoryAttribute objects."
		)
		
	# First, find category attribute whose name is contained in the query param
	attribute = None
	filtered_list = [attribute for attribute in category_attributes if attribute.name.lower() in param.lower()]
	if len(filtered_list) > 0:
		attribute = filtered_list[0]

	if attribute is None:
		return Post.objects.all()
	parsers = {
		'select' : lambda x: parse_select_query_param(param, query_params, x),
		'input' : lambda x: parse_input_query_param(param, query_params, x),
		'none' : lambda x: Post.objects.all()
	}
	return parsers.get(attribute.input_widget, 'none')(attribute)

def parse_select_query_param(param, query_params, attribute):
	# Dynamic field lookups brought to you by: https://stackoverflow.com/questions/1227091/how-to-dynamically-provide-lookup-field-name-in-django-query
	values = query_params.getlist(param)
	print(values)
	Qr = reduce(lambda x, y: x | Q(**{'attributes__data__{0}'.format(param): y}), values, Q())
	return Post.objects.filter(Qr)

def parse_input_query_param(param, query_params, attribute):
	Qr = None
	if attribute.input_type in (CategoryAttribute.INPUT_TYPE_NUMBER, CategoryAttribute.INPUT_TYPE_DATE):
		# Filtering on category attribute number or date types should be done with min_{PARAM} or max_{PARAM}
		value = query_params.get(param)
		try:
			value = int(value)
		except ValueError:
			pass

		Qr = Q(
			**{'attributes__data__{0}__{1}'.format(attribute.name.lower(), 'gte' if 'min' in param else 'lte') : value}
		)
		return Post.objects.filter(Qr)

	if attribute.input_type in (CategoryAttribute.INPUT_TYPE_CHECKBOX, CategoryAttribute.INPUT_TYPE_TEXT):
		# Checkboxes and text should be | together
		param_value = query_params.getlist(param)
		Qr = reduce(lambda x, y: x | Q(**{'attributes__data__{0}'.format(attribute.name.lower()) : param_value}))
		return Post.objects.filter(Qr)

	return Post.objects.all()



