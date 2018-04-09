from rest_framework import serializers
from posts.models import Post, PostAttribute, Category, CategoryAttribute, PostImage
from posts.utils import DynamicFieldsModelSerializer

class PostAttributeSerializer(serializers.ModelSerializer):
	class Meta:
		model = PostAttribute
		fields = ('data',)

class PostPhotoSerializer(serializers.ModelSerializer):
	class Meta:
		model = PostImage
		fields = ('image', )

class PostSerializer(DynamicFieldsModelSerializer):
	attributes = PostAttributeSerializer(many=True, required=False)
	photos = PostPhotoSerializer(many=True, required=False)
	class Meta:
		model = Post 
		fields = '__all__'
		read_only_fields = ('create_date', 'poster', 'photos', )

	def create(self, validated_data):
		post_attributes_data = validated_data.pop('attributes', None)
		post = Post.objects.create(**validated_data)
		if post_attributes_data is not None:
			for post_attribute in post_attributes_data:
				PostAttribute.objects.create(post=post, **post_attribute)	
		return post 

class CategoryAttributeSerializer(serializers.ModelSerializer):
	class Meta:
		model = CategoryAttribute 
		fields = '__all__'

class CategorySerializer(DynamicFieldsModelSerializer):
	attributes = CategoryAttributeSerializer(source='get_all_attributes', many=True)
	
	class Meta:
		model = Category
		fields = '__all__'