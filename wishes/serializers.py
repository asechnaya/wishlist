# wishes/serializers.py
from rest_framework import serializers
from djmoney.models.fields import MoneyField as DRFMoneyField # NEW: Import DRF MoneyField
from .models import Wish, Tag, User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class WishSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tags_input = serializers.CharField(write_only=True, required=False)
    # ИЗМЕНЕНО: Используем DRFMoneyField для поля 'price'
    price = DRFMoneyField()

    class Meta:
        model = Wish
        fields = [
            'id', 'user', 'title', 'image', 'price', 'shop_link',
            'description', 'created_at', 'private', 'completed', 'tags', 'tags_input'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        tags_input_data = validated_data.pop('tags_input', '')
        wish = Wish.objects.create(**validated_data)
        self._handle_tags(wish, tags_input_data)
        return wish

    def update(self, instance, validated_data):
        tags_input_data = validated_data.pop('tags_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_input_data is not None:
            self._handle_tags(instance, tags_input_data)
        return instance