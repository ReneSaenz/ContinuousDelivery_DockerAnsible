from rest_framework import serializers
from todo.models import TodoItem

class TodoItemSerailizer(serializers.HyperlinkedModelSerializer):
    url = serializers.ReadOnlyField()
    class Meta:
        model = TodoItem
        fields = ('url', 'title', 'completed', 'order')    
