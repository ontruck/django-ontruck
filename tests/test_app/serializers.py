from rest_framework import serializers

from .models import FooModel


class FooSerializer(serializers.ModelSerializer):

    class Meta:
        model = FooModel
        fields = ['title', 'pre_serializer']
