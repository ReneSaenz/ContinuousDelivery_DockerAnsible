from django.conf.urls import url, include
from todo import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it
"""
trailing_slash=False means Django will expect
- http://localhost/todos
- http://localhost/todos/15

trailing_slash=True means Django will expect
- http://localhost/todos/
- http://localhost/todos/15/

"""
router = DefaultRouter(trailing_slash=False)
router.register(r'todos', views.TodoItemViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
  url(r'^', include(router.urls)),
]
