from django.contrib import admin
from posts.models import Post, PostAttribute, PostImage, Category, CategoryAttribute 
# Register your models here.
admin.site.register(Post)
admin.site.register(PostAttribute)
admin.site.register(PostImage)
admin.site.register(Category)
admin.site.register(CategoryAttribute)