from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

class Post(models.Model):
	title = models.CharField(max_length=400)
	detail = models.TextField()
	poster = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	category = models.ForeignKey('posts.Category', on_delete=models.CASCADE)
	create_date = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=False)

	class Meta:
		ordering = ['-create_date']

	def __str__(self):
		return self.title

class PostAttribute(models.Model):
	post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name="attributes")
	data = JSONField()

	def __str__(self):
		return '{0} {1}'.format(self.post.title, self.data)

def upload_post_image(instance, filename):
	return 'post_{0}/{1}'.format(instance.post.id, filename)

class PostImage(models.Model):
	post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name="photos")
	image = models.FileField(upload_to=upload_post_image)

class Category(models.Model):
	short_name = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=128)
	parent_category = models.ForeignKey('posts.Category', related_name="sub_categories", null=True, blank=True, on_delete=models.SET_NULL)

	def get_all_sub_categories(self, include_self=True):
		cats = []
		if include_self:
			cats = cats + [self]
		for sub in Category.objects.filter(parent_category=self):
			cats = cats + sub.get_all_sub_categories(include_self=True)
		return cats

	def get_all_attributes(self):
		attributes = list(self.attributes.all())
		if self.parent_category is not None:
			attributes = attributes + self.parent_category.get_all_attributes()
		return attributes 

	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name

class CategoryAttribute(models.Model):
	INPUT_WIDGETS = (
		('select', 'select'),
		('textarea', 'textarea'),
		('input', 'input'),
	)
	INPUT_TYPE_TEXT = 'text'
	INPUT_TYPE_NUMBER = 'number'
	INPUT_TYPE_CHECKBOX = 'checkbox'
	INPUT_TYPE_DATE = 'date'
	INPUT_TYPES = (
		(INPUT_TYPE_TEXT, INPUT_TYPE_TEXT),
		(INPUT_TYPE_NUMBER, INPUT_TYPE_NUMBER),
		(INPUT_TYPE_CHECKBOX, INPUT_TYPE_CHECKBOX),
		(INPUT_TYPE_DATE, INPUT_TYPE_DATE),
	)
	category = models.ForeignKey('posts.Category', related_name="attributes", on_delete=models.CASCADE)
	name = models.CharField(max_length=128)
	unit = models.CharField(max_length=64, null=True, blank=True)
	is_mandatory = models.BooleanField(default=False)
	input_widget = models.CharField(max_length=128, choices=INPUT_WIDGETS)
	input_type = models.CharField(max_length=128, choices=INPUT_TYPES, blank=True, null=True)
	# For use if input_widget is a select box
	input_values = JSONField(blank=True, null=True)



