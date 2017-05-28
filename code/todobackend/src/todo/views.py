from django.shortcuts import render
from todo.models import TodoItemSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import list_route

# Create your views here.
# inherit from viewsets.ModelViewSet has default functionality on how to respond
# to each API request, based on model data
class TodoItemViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

    # override
    def perform_create(self, serializer):
        # save instance to get primary key and then update urls
        instance = serializer.save()
        # the following line will generate
        # http://<fqdn>:<port>/todos/<primary key>
        # http://localhost:8000/todos/14
        instance.url = reverse('todoitem-detail', args=[instance.ok], request=self.request)
        # persist the updated item
        instance.save()


    # functionality to delete all todos
    # This functionality is dangerous!
    def delete(self, request):
        TodoItem.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
