from django.urls import path
from posts.views import *

# Prefixed with api/
urlpatterns = [
	path('posts/<int:pk>/photos/', post_photo_create_view, name="photo_create"),
	path('posts/<int:pk>', PostRetrieveView.as_view(), name="post_get"),
	path('posts/', PostCreateView.as_view(), name="post_create"),
	path('categories/', CategoryListView.as_view(), name="categories"),
	path('categories/<str:pk>/', CategoryRetrieveView.as_view(), name="category"),
	path('search/', SearchView.as_view(), name='search'),
]